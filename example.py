from conan_build_tool import *
from conan_build_tool.Configurators import *

# define custom function to modify a build configuration



def ubuntu18_build(config):
    #set GCC Version 7.0, with C11 ABI
    GccConfigurator(7, use_cxx11_abi=True).configure(config)

    #Build in docker container
    DockerConfigurator("av3m/conan_ubuntu:18.04").configure(config)

    #set build type release
    BuildTypeConfigurator("Release").configure(config)
    return config


def android_build(config):
    return Av3mDockerAndroidConfigurator("24", "arm64", "clang").configure(config)


def windows_build(config):
    #set Compiler to MSVC 2010
    MsvcConfigurator("10").configure(config)

    #
    DockerConfigurator(None).configure(config)
    return config

packages = []
boost = create_config(None, "boost/1.67.0@conan/stable")
bzip2 = create_config(None, "bzip2/1.0.6@conan/stable")
zlib = create_config(None,  "zlib/1.2.11@conan/stable")

packages.append(bzip2)
packages.append(zlib)
packages.append(boost)





# set compiler settings of all packages to ubuntu 14.04 build
# (for all configs, defined method will be called)
set_configs(packages, android_build)
#set_configs(packages, ConanServerConfigurator(name="conan-center", url=None, user=None, password=None).configure)



# for all configs, create new configs with Windows settings
#append_configs(packages, windows_build)

print(packages)

# for all configs, create new configs with debug build typ
dbg = BuildTypeConfigurator("Debug")
append_configs(packages, dbg.configure)

for p in packages:
    build(p)
