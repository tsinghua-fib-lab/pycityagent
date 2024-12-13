#!/bin/bash

set -e

SYNCER_VERSION="v3.1.2"
ROUTING_VERSION="v2.0.6"
SIMULETGO_VERSION="v1.1.0"

# 解析用户输入的用户名和密码，在没有输入时，提示用户输入
echo "login to git.fiblab.net"
read -p "Please input your username: " username
read -s -p "Please input your Person Access Token: " access_token

# 下载安装二进制文件到~/.local/

# syncer
curl --user "$username:$access_token" \
     --fail \
     --location \
     "https://git.fiblab.net/api/v4/projects/14/packages/generic/syncer/$SYNCER_VERSION/syncer" \
     --output ~/.local/bin/syncer
chmod +x ~/.local/bin/syncer
echo "syncer installed successfully!"
echo "you can check it by running:
    ~/.local/bin/syncer -h"

# routing
curl --user "$username:$access_token" \
     --fail \
     --location \
     "https://git.fiblab.net/api/v4/projects/13/packages/generic/routing/$ROUTING_VERSION/routing_linux_amd64" \
     --output ~/.local/bin/routing
chmod +x ~/.local/bin/routing
echo "routing installed successfully!"
echo "you can check it by running:
    ~/.local/bin/routing -h"

# simuletgo
curl --user "$username:$access_token" \
     --fail \
     --location \
     "https://git.fiblab.net/api/v4/projects/25/packages/generic/simulet-go/$SIMULETGO_VERSION/simulet-go_linux_amd64" \
     --output ~/.local/bin/simulet-go
chmod +x ~/.local/bin/simulet-go
echo "simuletgo installed successfully!"
echo "you can check it by running:
    ~/.local/bin/simulet-go -h"
echo "ATTENTION: you should check the following dependencies to make sure simulet-go can run:
  - OS: Ubuntu 22.04 (if not, you should build from source or use softlink to make the following dynamic library available)
  - libproj-dev (apt install -y libproj-dev), if the OS is not Ubuntu 22.04, you should install it and then run \`ln -s libproj.so libproj.so.22\` in the LD_LIBRARY_PATH directory
  - libc.so.6 (make sure the version of GLIBC is 2.34 or higher)
