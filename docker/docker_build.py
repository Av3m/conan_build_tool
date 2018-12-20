#!/usr/bin/env python3
import subprocess

def docker_build(dockerfile, tagname, build_args=dict(), upload=False):
	docker_cmd  = ["docker", "build", "-f", dockerfile, "-t", tagname, "." ]

	for key,val in build_args.items():
		docker_cmd += [ "--build-arg", "%s=%s" % (key, val)]

	subprocess.check_call(docker_cmd)

	if upload:
		docker_upload_cmd = ["docker", "push", tagname]
		subprocess.check_call(docker_upload_cmd)


def docker_android_toolchain(arch, api,upload=False):
	docker_build("conan_android_toolchain", "av3m/conan_android_toolchain:{arch}_api{api}".format(arch=arch, api=api), {
		"NDK_API": api,
		"NDK_ARCH": arch
		},upload)

if __name__ == "__main__":
	apis = [
		"23", #6.0 Marshmallow
		"24", #7.0 Nougat
		"26", #8.0 Oreo
		"27" #8.1 Oreo
	]

	archs = [
		"arm",
		"arm64"
	]

	docker_build("conan_android_ndk", "av3m/conan_android_ndk:r18b",dict(), False)

	for arch in archs:
		for api in apis:
			docker_android_toolchain(arch, api,False)