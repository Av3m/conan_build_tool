# Conan Build Tool
## Summary
this python scripts is developed to automate package creation of conan.io packages.

## Features
* comfortable creation of build configs for different settings / options
* automatic building of packages out of locally available conanfile.py
* automatic building of packages inside a docker container
* support for android build profiles
* pre-configured docker build environments for android, ubunutu and even windows
* automatic upload of packages to custom servers

## Example usage
```
from conan_build_tool import *

#define custom function to modify a build configuration
def ubuntu14_build(config):
  set_gcc5(config)
  set_docker(config,"my_ubuntu14_docker_image")
  set_build_type(config,"Release")
  
def windows_build(config):
  set_msvc10(config)
  set_docker(config,None)

packages = []
boost = create_config(None,"boost/1.67.0@conan/stable")
bzip2 = create_config(None,"bzip2/1.0.6@conan/stable")
zlib = create_config(None,"zlib/1.2.11@conan/stable")

packages.append(boost)
packages.append(bzip2)
packages.append(zlib)




#set compiler settings of all packages to ubuntu 14.04 build
#(for all configs, defined method will be called)
set_config(packages,ubuntu14_build)


#for all configs, create new configs with Windows settings
append_config(packages,windows_build)


#for all configs, create new configs with debug build type
append_config(packages,set_build_type,"Debug")

for p in packages:
  build(p)  
```


