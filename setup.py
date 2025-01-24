import os
import platform
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
import stat

PACKAGE_NAME = "pycityagent"

BIN_SOURCES = {
    "pycityagent-sim": {
        "linux_x86_64": "https://git.fiblab.net/api/v4/projects/195/packages/generic/socialcity-sim/v1.0.6/socialcity-sim-noproj-linux-amd64",
        "darwin_arm64": "https://git.fiblab.net/api/v4/projects/195/packages/generic/socialcity-sim/v1.0.6/socialcity-sim-noproj-darwin-arm64",
    },
    "pycityagent-ui": {
        "linux_x86_64": "https://git.fiblab.net/api/v4/projects/188/packages/generic/socialcity-web/v0.3.1/socialcity-web-linux-amd64",
        "darwin_arm64": "https://git.fiblab.net/api/v4/projects/188/packages/generic/socialcity-web/v0.3.1/socialcity-web-darwin-arm64",
    },
}


class BinExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])
        self.name = name


class DownloadBin(build_ext):
    def run(self):
        system = platform.system()
        machine = platform.machine()
        auth = os.environ.get("GITLAB_AUTH")
        if not auth:
            print("No authentication provided for downloading binaries, please set GITLAB_AUTH=username:token")
            raise Exception("No authentication provided for downloading binaries, please set GITLAB_AUTH=username:token")
        else:
            auth = tuple(auth.split(":"))
            if len(auth) != 2:
                print("Invalid authentication provided for downloading binaries, please set GITLAB_AUTH=username:token")
                raise Exception("Invalid authentication provided for downloading binaries, please set GITLAB_AUTH=username:token")
        if system == "Linux":
            plat_dir = "linux"
            if machine == "x86_64":
                arch = "x86_64"
            else:
                print("Unsupported architecture on Linux")
                raise Exception("Unsupported architecture on Linux")
        elif system == "Darwin" and machine.startswith("arm"):
            plat_dir = "darwin"
            arch = "arm64"
        else:
            print("Unsupported platform")
            raise Exception("Unsupported platform")
        # build the extension
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(PACKAGE_NAME)))
        for ext in self.extensions:
            self.download_bin(
                ext.name, plat_dir, arch, os.path.join(extdir, PACKAGE_NAME), auth
            )

    def download_bin(self, binary_name, plat_dir, arch, bin_dir, auth):
        import requests
        import os

        url = BIN_SOURCES[binary_name].get(f"{plat_dir}_{arch}")
        if url:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                binary_path = os.path.join(bin_dir, binary_name)
                binary_path = os.path.abspath(binary_path)
                # print("try to download binary to", binary_path, flush=True)
                with open(binary_path, "wb") as f:
                    f.write(response.content)
                os.chmod(binary_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                print(f"Downloaded {binary_name} to {binary_path}")
            else:
                print(f"Download failed for {binary_name}")
                raise Exception(f"Download failed for {binary_name}")
        else:
            print(f"No binary found for {binary_name}")
            raise Exception(f"No binary found for {binary_name}")

setup(
    ext_modules=[BinExtension("pycityagent-sim"), BinExtension("pycityagent-ui"),],
    cmdclass=dict(build_ext=DownloadBin),
)

# # How to run it to build the distribution package
# pip install build
# GITLAB_USER=username GITLAB_PASS=token python -m build
#
# use cibuildwheel to build wheels for multiple platforms
# pip install cibuildwheel
# CIBW_ENVIRONMENT=GITLAB_AUTH=username:token cibuildwheel
