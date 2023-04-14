import json

from locust import HttpUser, task, between

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
        # param = json.loads("/home/dremacs/Dropbox/2023/sem8/P8/backend/scalability_tests/v2_req.json")

        with open("/home/dremacs/Dropbox/2023/sem8/P8/backend/scalability_tests/v2_req.json") as f:
            param = json.load(f)

        response = self.client.post("/api/v2/schedules", json=param)

        if response.status_code != 200:
            print(f"Failed request with status code: {response.status_code}, content: {response.content}")