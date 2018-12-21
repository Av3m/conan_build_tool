class CompilerConfigurator(object):
    def __init__(self, compiler, version, runtime, os_build, os, libcxx):
        self.compiler = compiler
        self.version = version
        self.runtime = runtime
        self.os_build = os_build
        self.os = os
        self.libcxx = libcxx

    def configure(self, params):
        params["settings"]["compiler"] = self.compiler
        params["settings"]["compiler.version"] = self.version

        if self.libcxx:
            params["settings"]["compiler.libcxx"] = self.libcxx

        if self.runtime:
            params["settings"]["compiler.runtime"] = self.runtime

        params["settings"]["os"] = self.os
        params["settings"]["os_build"] = self.os_build
        return params


class MsvcConfigurator(CompilerConfigurator):
    def __init__(self, version):
        CompilerConfigurator.__init__(self, "Visual Studio", str(version), "MD", "Windows", "Windows", None)


class GccConfigurator(CompilerConfigurator):

    cxx_abi_11 = "libstdc++11"
    cxx_abi = "libstdc++"

    def __init__(self, version, use_cxx11_abi=True):

        if use_cxx11_abi:
            str_cxx = GccConfigurator.cxx_abi_11
        else:
            str_cxx = GccConfigurator.cxx_abi

        CompilerConfigurator.__init__(self, "gcc", str(version), None, "Linux", "Linux", str_cxx)
