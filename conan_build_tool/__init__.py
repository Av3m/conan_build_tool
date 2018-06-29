import subprocess
import os
import sys
import copy
import re
import platform
import tempfile
import shutil
from colorama import Fore, Back, Style

from . import execution_script


default_params={
    "conanfile_path": "",
    "conan_user_home": os.path.expanduser("~"),
    
    "recipe_name": "",

    "skip_existing": True,
    
    "upload_server": None,
    
    "settings": {
        "arch": "x86_64",
        "build_type": "Release"
    },
    "options":{
        
    },
    "environment_variables":{
    },
    "misc_flags": [],
    "docker_image": {
        "name": None,
        "is_windows": False,
        "python_command": "python3"
    },
    
    "server_configs": []
    
}

def set_configs(params, mod_function, *mod_function_args):
    for p in params:
        mod_function(p,*mod_function_args)
    

        
def append_configs(params, mod_function, *mod_function_args):
    new_params = []
    for p in params:
        new_p = copy.deepcopy(p)
        new_params.append(mod_function(new_p,*mod_function_args))
        
    params += new_params
    
def add_server_config(params,name,url,user,password):
    config = dict()
    config["url"] = url
    config["name"] = name
    config["user"] = user
    config["password"] = password
    params["server_configs"].append(config)
    
def set_build_type(params,build_type):
    params["settings"]["build_type"] = build_type
    return params
    
def create_config(workdir,recipe_name,params=default_params):
    params = copy.deepcopy(params)
    params["conanfile_path"] = workdir
    params["recipe_name"] = recipe_name
    return params
    
def set_docker(params, docker_name, is_windows=False,python_command="python3"):
    params["docker_image"]["name"] = docker_name
    params["docker_image"]["is_windows"] = is_windows
    params["docker_image"]["python_command"] = python_command
    return params
    
def set_msvc10(params):
    params["settings"]["compiler"] = "Visual Studio"
    params["settings"]["compiler.version"] = "10"
    params["settings"]["compiler.runtime"] = "MD"
    return params

def set_gcc49(params):
    params["settings"]["compiler"] = "gcc"
    params["settings"]["compiler.version"] = "4.9"
    return params
    
def set_gcc48(params):
    params["settings"]["compiler"] = "gcc"
    params["settings"]["compiler.version"] = "4.8"
    return params
    
def set_gcc5(params):
    params["settings"]["compiler"] = "gcc"
    params["settings"]["compiler.version"] = "5"
    return params
    
    

def get_docker_ostype():
        docker_info = subprocess.check_output("docker info")
        
        if sys.version_info[0] == 2:
            m = re.search(r"OSType:\s*(.+)\s*",str(docker_info))
        else:
            m = re.search(r"OSType:\s*(.+)\s*",str(docker_info,encoding="ASCII"))
        if m == None: raise Exception("could not get OSType of Docker")
        return m.group(1)

def switch_docker(param):
    docker_os_type = get_docker_ostype()
    if ( (param["docker_image"]["is_windows"]) and (docker_os_type != "windows") ) or ( (param["docker_image"]["is_windows"] == False) and (docker_os_type == "windows") ):
        if ( platform.system() == "Windows"):
            print("Switching Docker OS")
            subprocess.check_call([os.path.join(os.getenv("ProgramFiles"),"Docker\Docker\DockerCli.exe"),'-SwitchDaemon'])

        else:
            raise Exception("Calling Docker Container with different os than your host is currently not supported!")

def add_docker_mount_conan_user_home(params):
    if not params["conan_user_home"]:
        return []

    conan_user_home = params["conan_user_home"]
    conan_user_home = os.path.abspath(conan_user_home)

    docker_conan_user_home = "/opt/conan_user_home"
    if (params["docker_image"]["is_windows"]):
        docker_conan_user_home = "C:\\temp\\conan_user_home"
    
    params["conan_user_home"] = docker_conan_user_home
    return ["-v",conan_user_home + ":" + docker_conan_user_home]

def add_docker_mount_conanfile_path(params):
    conanfile_path = params["conanfile_path"]
    if not conanfile_path:
        return []

    conanfile_path = os.path.abspath(conanfile_path)

    docker_conanfile_path =  "/opt/conan_recipe"
    if params["docker_image"]["is_windows"]:
        docker_conanfile_path = "C:\\temp\\conan_recipe"

    params["conanfile_path"] = docker_conanfile_path
    return ["-v",conanfile_path + ":" + docker_conanfile_path ]

def build(params):
    if params["conanfile_path"]:
        conanfile_path = os.path.abspath(params["conanfile_path"])
    else:
        conanfile_path = None

    conan_user_home = os.path.abspath(params["conan_user_home"])

    if (params["docker_image"]["name"]):
        if platform.system() == "Linux" and params["docker_image"]["is_windows"]:
            print(">>>> ERROR: RUNNING WINDOWS DOCKER IMAGE ON LINUX CURRENTLY NOT SUPPORTED! <<<")
            return

        switch_docker(params)
        
        docker_mounts = []
        docker_mounts += add_docker_mount_conanfile_path(params)
        docker_mounts += add_docker_mount_conan_user_home(params)
        
        script = execution_script.execution_script.format(params)
        
        print(">>>>> RUNNING DOCKER IMAGE %s <<<<<" %(params["docker_image"]["name"]))
        docker_command = ["docker","run", "-t"] + docker_mounts + [params["docker_image"]["name"],params["docker_image"]["python_command"],"-c",script]
        subprocess.check_call(docker_command)
    else:
        script = execution_script.format(params)
        subprocess.check_call(["python","-c",script])
    
    if (params["upload_server"]):
        subprocess.check_call(["conan","upload","--all","-r", params["upload_server"], params["recipe_name"]])
    
    
    
    
    
