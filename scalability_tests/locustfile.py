from locust import HttpUser, task, between
from generate_json import generate_json
import json

class ScalabilityTester(HttpUser):
    wait_time = between(1,5)

    @task(0)
    def v1_schedules(self):
        param = {"duration": 100, "power": 1}
        response = self.client.post("/api/v1/schedules", json=param)

        if response.status_code != 200:
            print(f"Failed request with status code: {response.status_code}, content: {response.content}")

    @task(1)
    def v2_schedules(self):
        # with open("/home/dremacs/Dropbox/2023/sem8/P8/backend/scalability_tests/v2_req.json") as f:
        #     param = json.load(f)

        # param = json.loads(generate_json())

        param = {
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


        response = self.client.post("/api/v2/schedules", json=param)

        if response.status_code != 200:
            print(f"Failed request with status code: {response.status_code}, content: {response.content}")
