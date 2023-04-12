from locust import HttpUser, task, between

class HelloWorldUser(HttpUser):
    wait_time = between(1,3)

    @task
    def hello_world(self):
        param = {"duration": 100, "power": 1}
        response = self.client.post("/api/v1/schedules", json=param)

        if response.status_code != 200:
            print(f"Failed request with status code: {response.status_code}, content: {response.content}")
