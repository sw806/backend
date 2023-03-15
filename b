usage: mypy [-h] [-v] [-V] [more options; see below]
            [-m MODULE] [-p PACKAGE] [-c PROGRAM_TEXT] [files ...]

Mypy is a program that will type check your Python code.

Pass in any files or folders you want to type check. Mypy will
recursively traverse any provided folders to find .py files:

    $ mypy my_program.py my_src_folder

For more information on getting started, see:

- http://mypy.readthedocs.io/en/latest/getting_started.html

For more details on both running mypy and using the flags below, see:

- http://mypy.readthedocs.io/en/latest/running_mypy.html
- http://mypy.readthedocs.io/en/latest/command_line.html

You can also use a config file to configure mypy instead of using
command line flags. For more details, see:

- http://mypy.readthedocs.io/en/latest/config_file.html

Optional arguments:
  -h, --help                Show this help message and exit
  -v, --verbose             More verbose messages
  -V, --version             Show program's version number and exit

Config file:
  Use a config file instead of command line arguments. This is useful if you
  are using many flags or want to set different options per each module.

  --config-file CONFIG_FILE
                            Configuration file, must have a [mypy] section
                            (defaults to mypy.ini, .mypy.ini, setup.cfg,
                            ~/.config/mypy/config, ~/.mypy.ini)
  --warn-unused-configs     Warn about unused '[mypy-<pattern>]' config
                            sections (inverse: --no-warn-unused-configs)

Import discovery:
  Configure how imports are discovered and followed.

  --namespace-packages      Support namespace packages (PEP 420, __init__.py-
                            less) (inverse: --no-namespace-packages)
  --ignore-missing-imports  Silently ignore imports of missing modules
  --follow-imports {normal,silent,skip,error}
                            How to treat imports (default normal)
  --python-executable EXECUTABLE
                            Python executable used for finding PEP 561
                            compliant installed packages and stubs
  --no-site-packages        Do not search for installed PEP 561 compliant
                            packages
  --no-silence-site-packages
                            Do not silence errors in PEP 561 compliant
                            installed packages

Platform configuration:
  Type check code assuming it will be run under certain runtime conditions.
  By default, mypy assumes your code will be run using the same operating
  system and Python version you are using to run mypy itself.

  --python-version x.y      Type check code assuming it will be running on
                            Python x.y
  -2, --py2                 Use Python 2 mode (same as --python-version 2.7)
  --platform PLATFORM       Type check special-cased code for the given OS
                            platform (defaults to sys.platform)
  --always-true NAME        Additional variable to be considered True (may be
                            repeated)
  --always-false NAME       Additional variable to be considered False (may be
                            repeated)

Disallow dynamic typing:
  Disallow the use of the dynamic 'Any' type under certain conditions.

  --disallow-any-unimported
                            Disallow Any types resulting from unfollowed
                            imports
  --disallow-any-expr       Disallow all expressions that have type Any
  --disallow-any-decorated  Disallow functions that have Any in their
                            signature after decorator transformation
  --disallow-any-explicit   Disallow explicit Any in type positions
  --disallow-any-generics   Disallow usage of generic types that do not
                            specify explicit type parameters (inverse:
                            --allow-any-generics)
  --disallow-subclassing-any
                            Disallow subclassing values of type 'Any' when
                            defining classes (inverse: --allow-subclassing-
                            any)

Untyped definitions and calls:
  Configure how untyped definitions and calls are handled. Note: by default,
  mypy ignores any untyped function definitions and assumes any calls to
  such functions have a return type of 'Any'.

  --disallow-untyped-calls  Disallow calling functions without type
                            annotations from functions with type annotations
                            (inverse: --allow-untyped-calls)
  --disallow-untyped-defs   Disallow defining functions without type
                            annotations or with incomplete type annotations
                            (inverse: --allow-untyped-defs)
  --disallow-incomplete-defs
                            Disallow defining functions with incomplete type
                            annotations (inverse: --allow-incomplete-defs)
  --check-untyped-defs      Type check the interior of functions without type
                            annotations (inverse: --no-check-untyped-defs)
  --disallow-untyped-decorators
                            Disallow decorating typed functions with untyped
                            decorators (inverse: --allow-untyped-decorators)

None and Optional handling:
  Adjust how values of type 'None' are handled. For more context on how mypy
  handles values of type 'None', see:
  http://mypy.readthedocs.io/en/latest/kinds_of_types.html#no-strict-
  optional

  --no-implicit-optional    Don't assume arguments with default values of None
                            are Optional (inverse: --implicit-optional)
  --no-strict-optional      Disable strict Optional checks (inverse: --strict-
                            optional)

Configuring warnings:
  Detect code that is sound but redundant or problematic.

  --warn-redundant-casts    Warn about casting an expression to its inferred
                            type (inverse: --no-warn-redundant-casts)
  --warn-unused-ignores     Warn about unneeded '# type: ignore' comments
                            (inverse: --no-warn-unused-ignores)
  --no-warn-no-return       Do not warn about functions that end without
                            returning (inverse: --warn-no-return)
  --warn-return-any         Warn about returning values of type Any from non-
                            Any typed functions (inverse: --no-warn-return-
                            any)
  --warn-unreachable        Warn about statements or expressions inferred to
                            be unreachable (inverse: --no-warn-unreachable)

Miscellaneous strictness flags:
  --allow-untyped-globals   Suppress toplevel errors caused by missing
                            annotations (inverse: --disallow-untyped-globals)
  --allow-redefinition      Allow unconditional variable redefinition with a
                            new type (inverse: --disallow-redefinition)
  --no-implicit-reexport    Treat imports as private unless aliased (inverse:
                            --implicit-reexport)
  --strict-equality         Prohibit equality, identity, and container checks
                            for non-overlapping types (inverse: --no-strict-
                            equality)
  --strict                  Strict mode; enables the following flags: --warn-
                            unused-configs, --disallow-any-generics,
                            --disallow-subclassing-any, --disallow-untyped-
                            calls, --disallow-untyped-defs, --disallow-
                            incomplete-defs, --check-untyped-defs, --disallow-
                            untyped-decorators, --no-implicit-optional,
                            --warn-redundant-casts, --warn-unused-ignores,
                            --warn-return-any, --no-implicit-reexport,
                            --strict-equality
  --disable-error-code NAME
                            Disable a specific error code
  --enable-error-code NAME  Enable a specific error code

Configuring error messages:
  Adjust the amount of detail shown in error messages.

  --show-error-context      Precede errors with "note:" messages explaining
                            context (inverse: --hide-error-context)
  --show-column-numbers     Show column numbers in error messages (inverse:
                            --hide-column-numbers)
  --show-error-codes        Show error codes in error messages (inverse:
                            --hide-error-codes)
  --pretty                  Use visually nicer output in error messages: Use
                            soft word wrap, show source code snippets, and
                            show error location markers (inverse: --no-pretty)
  --no-color-output         Do not colorize error messages (inverse: --color-
                            output)
  --no-error-summary        Do not show error stats summary (inverse: --error-
                            summary)
  --show-absolute-path      Show absolute paths to files (inverse: --hide-
                            absolute-path)

Incremental mode:
  Adjust how mypy incrementally type checks and caches modules. Mypy caches
  type information about modules into a cache to let you speed up future
  invocations of mypy. Also see mypy's daemon mode:
  mypy.readthedocs.io/en/latest/mypy_daemon.html#mypy-daemon

  --no-incremental          Disable module cache (inverse: --incremental)
  --cache-dir DIR           Store module cache info in the given folder in
                            incremental mode (defaults to '.mypy_cache')
  --sqlite-cache            Use a sqlite database to store the cache (inverse:
                            --no-sqlite-cache)
  --cache-fine-grained      Include fine-grained dependency information in the
                            cache for the mypy daemon
  --skip-version-check      Allow using cache written by older mypy version
  --skip-cache-mtime-checks
                            Skip cache internal consistency checks based on
                            mtime

Advanced options:
  Debug and customize mypy internals.

  --pdb                     Invoke pdb on fatal error
  --show-traceback, --tb    Show traceback on fatal error
  --raise-exceptions        Raise exception on fatal error
  --custom-typing-module MODULE
                            Use a custom typing module
  --custom-typeshed-dir DIR
                            Use the custom typeshed in DIR
  --warn-incomplete-stub    Warn if missing type annotation in typeshed, only
                            relevant with --disallow-untyped-defs or
                            --disallow-incomplete-defs enabled (inverse: --no-
                            warn-incomplete-stub)
  --shadow-file SOURCE_FILE SHADOW_FILE
                            When encountering SOURCE_FILE, read and type check
                            the contents of SHADOW_FILE instead.

Report generation:
  Generate a report in the specified format.

  --any-exprs-report DIR
  --cobertura-xml-report DIR
  --html-report DIR
  --linecount-report DIR
  --linecoverage-report DIR
  --lineprecision-report DIR
  --txt-report DIR
  --xml-report DIR
  --xslt-html-report DIR
  --xslt-txt-report DIR

Miscellaneous:
  --junit-xml JUNIT_XML     Write junit.xml to the given file
  --find-occurrences CLASS.MEMBER
                            Print out all usages of a class member
                            (experimental)
  --scripts-are-modules     Script x becomes module x instead of __main__

Running code:
  Specify the code you want to type check. For more details, see
  mypy.readthedocs.io/en/latest/running_mypy.html#running-mypy

  --explicit-package-bases  Use current directory and MYPYPATH to determine
                            module names of files passed
  --exclude PATTERN         Regular expression to match file names, directory
                            names or paths which mypy should ignore while
                            recursively discovering files to check, e.g.
                            --exclude '/setup\.py$'
  -m MODULE, --module MODULE
                            Type-check module; can repeat for more modules
  -p PACKAGE, --package PACKAGE
                            Type-check package recursively; can be repeated
  -c PROGRAM_TEXT, --command PROGRAM_TEXT
                            Type-check program passed in as string
  files                     Type-check given files or directories

Environment variables:
  Define MYPYPATH for additional module search path entries.
  Define MYPY_CACHE_DIR to override configuration cache_dir path.
