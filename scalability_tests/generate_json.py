import json
import time

# Emulates a user planning for washer, dryer, dishwasher, and TV

def generate_json():
    now = int(time.time())
    # now = 1682071200
    start_interval = {"start": now, "duration": 7200}
    end_interval = {"start": now + 14400, "duration": 7200}
    tasks = [
        {
            "duration": 13680,
            "power": 0.122,
            "must_start_between": [{"start_interval": start_interval}],
            "must_end_between": [{"end_interval": end_interval}],
            "id": "washer"
        },
        {
            "duration": 11280,
            "power": 0.536,
            "must_start_between": [{"start_interval": start_interval}],
            "must_end_between": [{"end_interval": {"start": now + 14400, "duration": 3600}}],
            "id": "dryer"
        },
        {
            "duration": 13800,
            "power": 0.141,
            "must_start_between": [{"start_interval": start_interval}],
            "must_end_between": [{"end_interval": {"start": now + 14400, "duration": 3600}}],
            "id": "dishwash"
        },
        {
            "duration": 7200,
            "power": 0.234,
            "must_start_between": [{"start_interval": start_interval}],
            "must_end_between": [{"end_interval": {"start": now + 14400, "duration": 3600}}],
            "id": "TV"
        }
    ]
    schedule = {"tasks": [], "maximum_power_consumption": {"maximum_consumption": 2}}
    data = {"tasks": tasks, "schedule": schedule}

    # save data to file
    with open("test.json", "w") as f:
        json.dump(data, f)

    return data
