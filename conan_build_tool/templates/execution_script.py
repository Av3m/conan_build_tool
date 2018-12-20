import subprocess
import os
import sys
import base64
import json
import shutil
import platform




def list_files(path):
    for root,folders,files in os.walk(path):
        for f in files:
            print(f)


def output_highlight(_str):
    print("="*len(_str))
    print(_str)
    print("="*len(_str))


def output_info(_str):
    print(">>>>>>>  " + _str)


def output_command(args):
    cmd_str = " ".join(args)
    output_info(cmd_str)


def check_conan_installation():
    conan_path = shutil.which("conan")
    if not conan_path:
        output_info("installing latest conan version")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--system", "conan"])


def check_existing_server(name):
    servers = get_conan_servers()
    return name in servers


def get_conan_servers():
    servers = []
    output = subprocess.check_output(["conan", "remote", "list"])
    output = str(output, encoding="ASCII")
    output = output.split("\n")
    for i in output:
        x = i.split(":")
        servers.append(x[0])

    return servers


def check_build_platform_compatibility(p):
    current_system = platform.system()

    return p["settings"]["os_build"] == current_system

    
def config_server(server_config):
    name = server_config["name"]
    url = server_config["url"]
    user = server_config["user"]
    password = server_config["password"]
    if check_existing_server(name):
        subprocess.check_call(["conan", "remote", "remove", name])

    if url:
        subprocess.check_call(["conan", "remote", "add", name, url])

    if user and password:
        subprocess.check_call(["conan", "user", "-r", name, user, "-p", password])
    
def build_local(params):
    args = get_commandline_params(params)
    conan_args = args["s"] + args["e"] + args["o"] + args["misc"]
    command = ["conan","create",".", conan_name] + conan_args
    output_command(command)
    subprocess.check_call(command,cwd=params["conanfile_path"])
    
def build_remote(params):
    args = get_commandline_params(params)
    conan_package_name = conan_name.split("/")[0]
    command = ["conan","install", conan_name] + args["s"] + args["o"] + args["e"] + ["--build=%s" %(conan_package_name) ]
    output_command(command)
    subprocess.check_call(command,cwd=params["conan_user_home"])

def get_commandline_params(params):
    settings = params["settings"]
    conan_args_s = []
    conan_args_o = []
    conan_args_e = []
    conan_args_misc = []
    for key,val in settings.items():
        conan_args_s += ["-s","%s=%s" % (key,val)]

    for key,val in params["options"].items():
        conan_args_o += ["-o","%s=%s" %(key,val)]

    for key,val in params["environment_variables"].items():
        conan_args_e += ["-e","%s=%s" %(key,val)]
        
    for val in params["misc_flags"]:
        conan_args_misc += [val]
        
    ret = {}
    ret["o"] = conan_args_o
    ret["s"] = conan_args_s
    ret["e"] = conan_args_e
    ret["misc"] = conan_args_misc
    
    return ret


def get_config_from_env():
    _conf = os.getenv("CONAN_BUILD_CONFIG", None)
    if not _conf:
        raise Exception("could not get build config from environment!")

    _conf = base64.b64decode(_conf)
    _conf = json.loads(_conf)
    return _conf
        
    
def check_existing_package(params):
    args = get_commandline_params(params)
    try:
        subprocess.check_call(["conan", "install", conan_name ] + args["s"] + args["e"] + ["--build=never"],cwd=params["conan_user_home"])
        return True
    except subprocess.CalledProcessError as e:
        return False
        
        
params = get_config_from_env()


if not check_build_platform_compatibility(params):
    output_info("skipping build. platforms do not match")
    sys.exit(0)


check_conan_installation()




server_configs = params["server_configs"]
for config in server_configs:
    config_server(config)



if not (params["conan_user_home"]):
   params["conan_user_home"] = os.path.expanduser("~")


os.environ["CONAN_USER_HOME"] = params["conan_user_home"]


#upgrade_conan()

default_profile = os.path.join(os.environ["CONAN_USER_HOME"],".conan","profiles","default")
if ( os.path.exists(default_profile)):
    os.remove(default_profile)
subprocess.check_call(["conan","profile","new","--detect","default"])


conan_name = params["recipe_name"]
docker_image = params["docker_image"]["name"]
upload_server = params["upload_server"]

#check if package is existing
is_existing = check_existing_package(params)


#build package
if not (is_existing and (params["skip_existing"] == True) ):
    output_highlight("BUILDING PACKAGE %s" %(conan_name))
    if ( params["conanfile_path"]):
        build_local(params)
    else:
        build_remote(params)
else:
    output_info("skipping build of %s, because requested package is already existing" %(conan_name))


if (upload_server):
    output_highlight("UPLOADING PACKAGE %s" %(conan_name))
    subprocess.check_call(["conan", "upload", "--all", "-r", upload_server, conan_name])
