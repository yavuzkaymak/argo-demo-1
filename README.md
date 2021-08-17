# argo-demo

The image installs argo-cd and argo-workflows in a given kubernetes cluster. 
Argo-cd is in argocd, argo-worklows is in argo namespaces created. Argo-cd by default listens to 
manifests/argo-workflow/workflows and implements the changes in this folder.

It deploys a sample workflow using a workflow template. Workflow consists of a dag which first 
executes a Talend Job and only if the Job fails executes a shell command in an alpine container.

The Talend job looks for "COOL_NAME". If the variable is not found "CIMT" will be used as default. If the
variable exists but as an empty string, it will throw an error which will trigger the second job.

The Talend job was created using Talend Open Studio and its image is found in docker hub 
vizgen/hello_word.

You can manipulate the variable using Argo Workflows' gui.

###  Docker Way

If you are new to the container technologies. I would recommend setting up docker-desktop and activating \
its Kubernetes feature.

Dont push this a repo. 

Important! The dockerfile copies the content of the kube config file which is registered \
in user's KUBECONFIG env variable. That means the container doesn't necessarily interact with the default config file found under home directory's .kube folder.\
It is so designed that those who organize environments based on directories will not end up messing another kubernetes cluster. 

Before building your image check the kubeconfig variable in your environment and make sure you
the path is correct:

echo $KUBECONFIG

Then build your own image:

docker build . -t <your_super_cool_tag>

docker run -rm -it <your_super_cool_tag>

That's it. You should see argo-cd url and credentials your screen.

Tipp: Instead of throwing your kubeconfig in the image, you can build your own image without kubeconfig file
and then mount your kubeconfig during execution of the docker image with -v flag.
