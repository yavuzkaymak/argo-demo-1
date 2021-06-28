#!/usr/bin/env bash

set -o pipefail

cd "$(dirname "$0")" || exit

argocd_manifest=https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
argoworkflow_manifet=https://raw.githubusercontent.com/argoproj/argo-workflows/stable/manifests/namespace-install.yaml

argoworkflow_labels="-l app=argo-server"
argocd_labels="--all"

function createNamespace() {

  output=$(kubectl create namespace "$1" 2>&1 >/dev/null)

  if [[ $output == *"AlreadyExists"* ]]; then
    echo "[INFO] $1 namespace exists, it won't be new created."; else
    echo "[INFO] $1 namespace has been created."
  fi
}

function installer() {
  #arg[1] -> namespace, arg[2] -> file to be applied, arg[3] flags to be followed in wait clause
  echo "[INFO] Deploying $1"
  kubectl apply -n "$1" -f "$2" >/dev/null && \
  kubectl wait --for=condition=Ready --timeout=120s pods -n "$1" "$3"  >/dev/null

  if [[ $1 -ne 0 ]]; then
    echo "[INFO] $1 could not be deployed"; else
    echo "[INFO] $1 has been deployed"
  fi
}

function getArgocdServer() {

  kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}' >/dev/null
  argocd_pass=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
  argocd_port=$(kubectl get svc argocd-server -n argocd -o jsonpath={.spec.ports[0].nodePort})

  echo "[INFO] ARGO-CD password is $argocd_pass"
  echo "[INFO] Argo-CD username is  admin"
  echo "[INFO] Argo-CD gui is accesible via https://localhost:$argocd_port"

}
function getArgoWorkflowServer() {

  kubectl patch svc argo-server -n argo -p '{"spec": {"type": "NodePort"}}' >/dev/null
  argo_port=$(kubectl get svc argo-server -n argo -o jsonpath={.spec.ports[0].nodePort})
  echo "[INFO] Argo-Workflow gui is accesible via https://localhost:$argo_port"

}

function applyARGOCDTemplate(){
  kubectl apply -f manifests/argo-cd/argo_cd_template.yaml >/dev/null
  if [[ $? -ne 0 ]]; then
    echo "[ERROR] ArgoCD template could not be applied. Exiting" && exit 1; else
    echo "[INFO] ArgoCD is listening to the changes in the Git Repo"
  fi
}

createNamespace argocd
createNamespace argo
installer argocd $argocd_manifest $argocd_labels
installer argo $argoworkflow_manifet "$argoworkflow_labels"
applyARGOCDTemplate
getArgoWorkflowServer
getArgocdServer

