#!/usr/bin/env bash

set -o pipefail

argocd_manifest=https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
argoworkflow_manifet=https://raw.githubusercontent.com/argoproj/argo-workflows/stable/manifests/namespace-install.yaml


function createNamespace() {

  output=$(kubectl create namespace "$1" 2>&1 >/dev/null)

  if [[ $output == *"AlreadyExists"* ]]; then
    echo "[INFO] $1 namespace exists, it won't be new created."; else
    echo "[INFO] $1 namespace has been created."
  fi
}

function installer() {
  #arg[1] -> namespace, arg[2] -> file to be applied
  echo "[INFO] Deploying $1"
  kubectl apply -n "$1" -f "$2" >/dev/null && \
  kubectl wait --for=condition=Ready --timeout=120s pods --all -n "$1" >/dev/null

  if [[ $1 -ne 0 ]]; then
    echo "[INFO] $1 could not be deployed"; else
    echo "[INFO] $1 has been deployed"
  fi
}


createNamespace argocd
createNamespace argo
installer argocd $argocd_manifest
installer argo $argoworkflow_manifet



