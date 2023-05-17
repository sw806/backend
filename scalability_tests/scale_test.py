from generate_json import generate_json
import json


if __name__ == "__main__":
    result = generate_json()
    result_json = json.dumps(result)
    print(result_json)
