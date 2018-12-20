import os
class ConanServerConfigurator(object):
    def __init__(self, name, url, user, password):
        self.name = name
        self.url = url
        self.user = user
        self.password = password

    @staticmethod
    def create_from_env():
        name = os.getenv("CONAN_SERVER_NAME", None)
        url = os.getenv("CONAN_SERVER_URL", None)
        user = os.getenv("CONAN_SERVER_USERNAME", None)
        password = os.getenv("CONAN_SERVER_PASSWORD", None)

        if not name or not url:
            raise Exception("could not get conan server configuration from environment!")

        return ConanServerConfigurator(name, url, user, password)

    def configure(self, params):
        config = dict()
        config["url"] = self.url
        config["name"] = self.name
        config["user"] = self.user
        config["password"] = self.password
        params["server_configs"].append(config)
        return params
