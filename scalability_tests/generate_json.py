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


def generate_json() -> str:
    data = {
        "tasks": [
            {
                "duration": random.randint(DURATION_MIN_RANGE, DURATION_MAX_RANGE),
                "power": random.uniform(POWER_MIN_RANGE, POWER_MAX_RANGE),
                "must_start_between": [
                    {
                        "start_interval": {
                            "start": random.randint(START_INTERVAL_START_MIN_RANGE, START_INTERVAL_START_MAX_RANGE), # 15:00
                            "duration": random.randint(START_INTERVAL_DURATION_MIN_RANGE, START_INTERVAL_DURATION_MAX_RANGE) # 00:30
                        }
                    }
                ],
                "must_end_between": [
                    {
                        "end_interval": {
                            "start": random.randint(END_INTERVAL_START_MIN_RANGE, END_INTERVAL_START_MAX_RANGE), # 16:00
                            "duration": random.randint(END_INTERVAL_DURATION_MIN_RANGE, END_INTERVAL_DURATION_MAX_RANGE) # 00:30
                        }
                    }
                ],
                "id": "string"
            }
        ],
        "schedule": {
            "tasks": [
                {
                    "task": {
                       "duration": random.randint(DURATION_MIN_RANGE, DURATION_MAX_RANGE),
                        "power": random.uniform(POWER_MIN_RANGE, POWER_MAX_RANGE),
                        "must_start_between": [
                        {
                        "start_interval": {
                            "start": random.randint(START_INTERVAL_START_MIN_RANGE, START_INTERVAL_START_MAX_RANGE), # 15:00
                            "duration": random.randint(START_INTERVAL_DURATION_MIN_RANGE, START_INTERVAL_DURATION_MAX_RANGE) # 00:30
                        }
                    }
                ],
                "must_end_between": [
                    {
                        "end_interval": {
                            "start": random.randint(END_INTERVAL_START_MIN_RANGE, END_INTERVAL_START_MAX_RANGE), # 16:00
                            "duration": random.randint(END_INTERVAL_DURATION_MIN_RANGE, END_INTERVAL_DURATION_MAX_RANGE) # 00:30
                        }
                    }
                ],
                "id": "string"
            },
                    "start_interval": {
                        "start": random.randint(START_INTERVAL_START_MIN_RANGE, START_INTERVAL_START_MAX_RANGE), # 15:00
                        "duration": random.randint(START_INTERVAL_DURATION_MIN_RANGE, START_INTERVAL_DURATION_MAX_RANGE)
                    },
                    "cost": random.randint(COST_MIN_RANGE, COST_MAX_RANGE)
                }
            ],
            "maximum_power_consumption": {
                "maximum_consumption": random.uniform(MAX_CONSUMPTION_MIN_RANGE, MAX_CONSUMPTION_MAX_RANGE)
            }
        }
    }
    return json.dumps(data)

if __name__ == "__main__":
    result = generate_json()
    print(result)
