#!/usr/bin/env bash

set -eo pipefail

git clone https://github.com/yavuzkaymak/argo-demo.git && \
chmod +x /opt/argo-demo/main.sh && \

/opt/argo-demo/main.sh