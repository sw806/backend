import datetime
import json
import random
import time

# specify the range of random numbers

DURATION_MIN_RANGE = 30
DURATION_MAX_RANGE = 180

POWER_MIN_RANGE = 0.5
POWER_MAX_RANGE = 2.5 # Miele

START_INTERVAL_START_MIN_RANGE = int(time.time())
START_INTERVAL_START_MAX_RANGE = int(time.time()) + 43200 # 12 hours
START_INTERVAL_DURATION_MIN_RANGE = 0
START_INTERVAL_DURATION_MAX_RANGE = 10800 # 3 hours (skøn)

END_INTERVAL_START_MIN_RANGE = int(time.time()) + 1
END_INTERVAL_START_MAX_RANGE = int(time.time()) + 43201 # 12 hours + 1 second
END_INTERVAL_DURATION_MIN_RANGE = 0
END_INTERVAL_DURATION_MAX_RANGE = 10800 # 3 hours (skøn)

COST_MIN_RANGE = 1
COST_MAX_RANGE = 10

MAX_CONSUMPTION_MIN_RANGE = 0.25
MAX_CONSUMPTION_MAX_RANGE = 7.5


def generate_json() -> str: # TODO add constant values
    data = {
    "tasks": [
        {
            "id": "2",
            "duration": 3600,
            "power": 1,
            "must_start_between": [],
            "must_end_between": []
        }
    ],
    "schedule": {
        "tasks": [
            {
                "task": {
                    "duration": 3600,
                    "power": 1.0,
                    "must_start_between": [],
                    "must_end_between": [],
                    "id": "1"
                },
                "start_interval": {
                    "start": 1681743600,
                    "duration": 0
                },
                "cost": 0.691
            }
        ],
        "maximum_power_consumption": {
            "maximum_consumption": 1
        }
    }
}

    return json.dumps(data)


if __name__ == "__main__":
    result = generate_json()
    print(result)
