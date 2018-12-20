class DockerConfigurator:
    def __init__(self, docker_name, is_windows=False, python_command="python3"):
        self.docker_name = docker_name
        self.is_windows = is_windows
        self.python_command = python_command

    def configure(self, params):
        params["docker_image"]["name"] = self.docker_name
        params["docker_image"]["is_windows"] = self.is_windows
        params["docker_image"]["python_command"] = self.python_command
        return params
