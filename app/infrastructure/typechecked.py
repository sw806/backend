from inspect import Parameter, Signature, signature
from inspect import isfunction
from typing import Any, Generic, TypeVar, get_args, get_origin


def typechecked(f):
    if not isfunction(f):
        raise TypeError("typechecked can only work on functions")

    def __annotation_to_type(annotation) -> Any:
        if annotation == Signature.empty:
            return Any
        return annotation

    def __test_types(obj, cls) -> bool:
        # Any type is accepted
        if cls == Any:
            return True

        # Check if object has generic arguments.
        if isinstance(obj, Generic):
            # Check if obj is directly an instance of the base class
            if isinstance(obj, get_origin(cls)):
                return True

            cls_generic_arguments = get_args(cls)
            obj_orig_bases = obj.__orig_bases__
            # Get all inherited classes of obj.
            for base in obj_orig_bases:
                # Check if the generic argument is "Generic[~T,]"
                base_origin = get_origin(base)
                if base_origin is Generic:
                    continue

                # Check the generic arguments that they match.
                obj_generic_arguments = get_args(base)
                if len(cls_generic_arguments) != len(obj_generic_arguments):
                    continue
                for idx, obj_generic_argument in enumerate(obj_generic_arguments):
                    if not issubclass(obj_generic_argument, cls_generic_arguments[idx]):
                        continue

                return True
            # Did not find a type match in the origin bases
            return False

        # print(f'Check: {obj}: {cls} is {type(obj)}')
        # Check generic typevar arguments.
        cls_type = type(cls)
        if cls_type is TypeVar:
            raise TypeError("TypeVar not supported")

        # Class constructors taking self as first parameter and is a member of another class.
        if obj == None and cls == None:
            return True

        return isinstance(obj, cls)

    def decorated(*args, **kwargs):
        function_definition = signature(f)
        formal_parameters = function_definition.parameters

        # Check positional arguments and keyword arguments (succeeding positionals).
        for idx, (formal_parameter_name, formal_parameter) in enumerate(formal_parameters.items()):
            formal_parameter_type = __annotation_to_type(formal_parameter.annotation)
            formal_parameter_default = formal_parameter.default
            # The actual parameter is defaults to None unless there is a default parameter.
            actual_parameter = None if formal_parameter_default == Parameter.empty else formal_parameter_default
            # 0: Default value was used, 1: position, 2: keyword.
            actual_parameter_placement = 0

            if idx < len(args): 
                # Positional.
                actual_parameter = args[idx]
                actual_parameter_placement = 1
            else:
                # Default value.
                if formal_parameter_name in kwargs:
                    # Keywords.
                    actual_parameter = kwargs[formal_parameter_name]
                    actual_parameter_placement = 2

            # Missing parameter.
            if actual_parameter is None:
                raise ValueError(f'Parameter "{formal_parameter_name}" is missing a value of type {formal_parameter_type}')

            actual_parameter_type = __annotation_to_type(actual_parameter)

            # print(f'Parameter: {formal_parameter_name}: {formal_parameter_type} is {type(actual_parameter)}')

            if not __test_types(actual_parameter, formal_parameter_type):
                if actual_parameter_placement == 0:
                    raise TypeError(f'Default value of parameter "{formal_parameter_name}" was not type {formal_parameter_type} instead it was {actual_parameter_type}')
                elif actual_parameter_placement == 1:
                    raise TypeError(f'Positional parameter "{formal_parameter_name}" was not type {formal_parameter_type} instead it was {actual_parameter_type}')
                elif actual_parameter_placement == 2:
                    raise TypeError(f'Keyword parameter "{formal_parameter_name}" was not type {formal_parameter_type} instead it was {actual_parameter_type}')

        # Check return value type.
        formal_return_type = __annotation_to_type(function_definition.return_annotation)
        return_value = f(*args, **kwargs)
        if not __test_types(return_value, formal_return_type):
            raise TypeError(f'The return value {return_value} was not type {formal_return_type} instead got {type(return_value)}')

        return return_value
    return decorated