# argo-demo

The image installs argo-cd and argo-workflows in a given kubernetes cluster. 
Argo-cd is in argocd, argo-worklows is in argo namespaces created. Argo-cd by default listens to 
manifests/argo-workflow/workflows and implements the changes in this folder.

It deploys a sample workflow using a workflow template. Workflow consists of a dag which first 
executes a Talend Job and only if the Job fails executes a shell command in an alpine container.

The Talend job looks for "COOL_NAME". If the variable is not found "CIMT"  be used as default. If the
variable exists but as an empty string, it will throw an error which will trigger the second job.

The Talend job was created using Talend Open Studio and its image is found in docker hub 
vizgen/hello.

You can manipulate the variable using Argo Workflows' gui.

If you are new to the container technologies. I would recommend setting up docker-desktop and activating \
   its Kubernetes feature.


## Installation

If you have already kubectl install:

1. check if you have the correct kubeconfig:

echo $KUBECONFIG

2. give exec rights to main.sh

chmod +x main.sh

3. Go ahead and deploy

./main.sh

