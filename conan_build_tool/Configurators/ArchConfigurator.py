class ArchConfigurator(object):
    def __init(self, arch_build, arch):
        self.arch = arch
        self.arch_build = arch_build

    def configure(self, params):
        params["settings"]["arch_build"] = self.arch_build
        params["settings"]["arch"] = self.arch
        return params

