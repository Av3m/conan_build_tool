class BuildTypeConfigurator(object):
    def __init__(self, build_type):
        self.build_type = build_type

    def configure(self, params):
        params["settings"]["build_type"] = self.build_type
        return params
