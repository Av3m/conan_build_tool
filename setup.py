import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conan_build_tool",
    version="0.0.1",
    author="Av3m",
    author_email="av3m@openmailbox.org",
    description="python script to automate package compilation of conan.io binary packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Av3m/conan_build_tool",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
