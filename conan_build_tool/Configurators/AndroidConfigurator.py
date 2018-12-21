from conan_build_tool.Configurators import DockerConfigurator


class AndroidConfigurator(object):
    def __init__(self, api_level, compiler, toolchain_path, arch):
        self.api_level = api_level
        self.arch = arch
        self.compiler = compiler
        self.toolchain_path = toolchain_path

    def getarch(self,arch_in):
        if arch_in == "arm":
            return "armv7"
        elif arch_in == "arm64":
            return "armv8"
        else:
            return arch_in

    def gettargethost(self):
        if self.arch == "arm":
            return "arm-linux-androideabi"
        elif self.arch == "arm64":
            return "aarch64-linux-android"

    def getcompilernames(self):
        if self.compiler == "gcc":
            return "gcc", "g++"

        elif self.compiler == "clang":
            return "clang", "clang++"
        else:
            raise Exception("not supported compiler")

    def getcflags(self):
        ret = ["-fPIC", "-fPIE", "-I%s/include/c++/4.9.x" % (self.toolchain_path,)]
        return ret

    def getcxxflags(self):
        return self.getcflags() + [ "-std=c++11" ]

    def getldflags(self):
        ret = ["-pie"]

        if self.arch == "arm64":
            ret.append("-fuse-ld=gold")

        return ret


    def getcompilerversion(self):

        if self.compiler == "gcc": return "4.9"
        elif self.compiler == "clang": return "7.0"
        else: raise Exception("not supported compiler")
    def configure(self, params):
        target = self.gettargethost()
        params["settings"]["os"] = "Android"
        params["settings"]["os_build"] = "Linux"
        params["settings"]["os.api_level"] = self.api_level
        params["settings"]["compiler"] = self.compiler
        params["settings"]["compiler.version"] = self.getcompilerversion()
        params["settings"]["compiler.libcxx"] = "libstdc++"
        params["settings"]["arch"] = self.getarch(self.arch)
        params["settings"]["build_type"] = "Release"

        params["environment_variables"]["CONAN_CMAKE_FIND_ROOT_PATH"] = self.toolchain_path + "/sysroot"
        params["environment_variables"]["PATH"] = "[%s/bin]" % (self.toolchain_path,)
        params["environment_variables"]["CHOST"] = target
        params["environment_variables"]["AR"] = target + "-ar"
        params["environment_variables"]["AS"] = target + "-as"
        params["environment_variables"]["RANLIB"] = target + "-ranlib"

        params["environment_variables"]["CC"] = target + "-" + self.getcompilernames()[0]
        params["environment_variables"]["CXX"] = target + "-" + self.getcompilernames()[1]
        params["environment_variables"]["LD"] = target + "-ld"
        params["environment_variables"]["STRIP"] = target + "-strip"

        params["environment_variables"]["CFLAGS"] = " ".join(self.getcflags())
        params["environment_variables"]["CXXFLAGS"] = " ".join(self.getcxxflags())
        params["environment_variables"]["LDFLAGS"] = " ".join(self.getldflags())

        return params


class Av3mDockerAndroidConfigurator(AndroidConfigurator):
    def __init__(self, api_level, arch, compiler="clang"):
        AndroidConfigurator.__init__(self, api_level, compiler, "/usr/local/android-toolchain", arch)

    def configure(self, params):
        params = AndroidConfigurator.configure(self, params)
        return DockerConfigurator("av3m/conan_android_toolchain:%s_api%s" % (self.arch, self.api_level)).configure(params)


