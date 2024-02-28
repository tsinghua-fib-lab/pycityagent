#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

pip3 install . -vv

rm -rf "${PROJECT_DIR}/build"
rm -rf "${PROJECT_DIR}/pycitysim.egg-info"
