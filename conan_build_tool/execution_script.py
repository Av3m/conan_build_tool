execution_script='''

import subprocess
import os
import sys
import platform
import tempfile
import shutil
from colorama import Fore, Back, Style

def list_files(path):
    for root,folders,files in os.walk(path):
        for f in files:
            print(f)

def upgrade_conan():
    python_command = sys.executable
    subprocess.check_call([python_command,"-m", "pip","install","--upgrade","conan==1.4.4" ])

def check_existing_server(name):
    servers = []
    output = subprocess.check_output(["conan","remote","list"])
    output = str(output,encoding="ASCII")
    output = output.split("\\n")
    for i in output:
        x = i.split(":")
        servers.append(x[0])
    return (name in servers)
    
def config_server(server_config):
    name = server_config["name"]
    url = server_config["url"]
    user = server_config["user"]
    password = server_config["password"]
    if check_existing_server(name):
        subprocess.check_call(["conan","remote","remove",name] )
    subprocess.check_call(["conan","remote","add",name,url ] )
    if ( user):
        subprocess.check_call(["conan","user","-r",name,user,"-p",password] )
    

def build_local(params):
    if ( platform.system() == "Windows" ):
        temp_dir = "C:\\conan_temp"
    else:
        temp_dir = "/opt/conan_temp"

    shutil.copytree(params["conanfile_path"],temp_dir)
    command = ["conan","create",".", conan_name] + conan_args
    subprocess.check_call(command,cwd=temp_dir)

params = {0}

conan_args_s = []
conan_args_o = []
conan_args_e = []
conan_args_misc = []


server_configs = params["server_configs"]
for config in server_configs:
    config_server(config)

settings = params["settings"]
for key,val in settings.items():
    conan_args_s += ["-s","%s=%s" % (key,val)]

for key,val in params["options"].items():
    conan_args_o += ["-o","%s=%s" %(key,val)]

for key,val in params["environment_variables"].items():
    conan_args_e += ["-e","%s=%s" %(key,val)]
    
for val in params["misc_flags"]:
    conan_args_misc += [val]

if not (params["conan_user_home"]):
   params["conan_user_home"] = os.path.expanduser("~")


os.environ["CONAN_USER_HOME"] = params["conan_user_home"]
conan_args = conan_args_s + conan_args_e + conan_args_o + conan_args_misc

#upgrade_conan()

default_profile = os.path.join(os.environ["CONAN_USER_HOME"],".conan","profiles","default")
if ( os.path.exists(default_profile)):
    os.remove(default_profile)
subprocess.check_call(["conan","profile","new","--detect","default"])


conan_name = params["recipe_name"]
docker_image = params["docker_image"]["name"]
upload_server = params["upload_server"]

#check if package is existing
is_existing = False
try:
    subprocess.check_call(["conan", "install", conan_name, ] + conan_args_s + conan_args_o + ["--build=never"],cwd=params["conan_user_home"] )
    is_existing = True
except subprocess.CalledProcessError as e:
    is_existing = False

#build package
if not (is_existing and (params["skip_existing"] == True) ):
    print(">>>>> BUILDING PACKAGE %s <<<<<" %(conan_name))
    if ( params["conanfile_path"]):
        build_local(params)
    else:
        conan_package_name = conan_name.split("/")[0]
        command = ["conan","install", conan_name] + conan_args_s + conan_args_o + conan_args_e + ["--build=%s" %(conan_package_name) ]
        subprocess.check_call(command,cwd=params["conan_user_home"] )
else:
    print(">>>>> SKIPPING BUILD OF %s, BECAUSE ALREADY EXISTING <<<<<" %(conan_name))


if (upload_server and docker_image and not params["conan_user_home"]):
    print(">>>>> UPLOADING PACKAGE %s <<<<<" %(conan_name))
    subprocess.check_call(["conan","upload","--all","-r",upload_server,conan_name])
'''
