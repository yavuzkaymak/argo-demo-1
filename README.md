# argo-demo

The image installs argo-cd and argo-workflows in given kubernetes cluster. 
Argo-cd is in argocd, argo-worklows in argo namespaces created. Argo-cd by default listens to 
manifests/argo-workflow/workflows and implements the changes in this folder.

### Usage Docker Way

Important! The dockerfile copies the content of the kube config file 
which is registered in user's KUBECONFIG env variable. That means the container doesn't necessarily interact with the default config file found under home directory's .kube folder.
It is so designed that those who organize environments based on directories 
will not end up messing another kubernetes cluster. 

An image is found in dockerhub

docker run -rm -it -v path/to/mykubeconfig:./kube vizgen/argo

Better way would be building your own image.

### Usage Python Way

Python script does the same as the docker container but in a slightly more interactive way.
The script offers a more secure way of interacting with the cluster. As it only accepts docker-desktop as cluster.

You should set in .env file KUBECONFIG var: for example KUBECONFIG=C:/Users/super_user/.kube/config
The script will check if docker-desktop is found in config and then it will ask user to config if the user has chosen the right cluster.

pip install -r requirements.txt
python3 main.py