# argo-demo

The image installs in argo-cd and argo-workflows in given kubernetes cluster. 
Argo-cd is in argocd, argo-worklows in argo namespaces created. Argo-cd by default listens to 
manifests/argo-workflow/workflows and implements the changes in this folder.

### Usage

Important! The dockerfile copies the content of the kube config file 
which is registered in user's KUBECONFIG env variable. That means the container doesn't necessarily interact with the default config file found under home directory's .kube folder.
It is so designed that those who organize env based on directories 
will not end up messing another kubernetes cluster. 

An image is found in dockerhub

docker run -rm -it vizgen/argo