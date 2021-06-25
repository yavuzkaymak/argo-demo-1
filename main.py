import base64
import logging
import os
import sys

from kubernetes import client, config, watch, utils
import dotenv
import yaml
import json


def loadYaml(file: str):
    with open(file=file) as fhandler:
        try:
            return list(yaml.safe_load_all(fhandler))
        except yaml.YAMLError as e:
            print(e)


# noinspection PyBroadException
def skip_if_already_exists(e, resource: str):
    info = json.loads(e.api_exceptions[0].body)
    if info.get('reason').lower() == 'alreadyexists':
        print("[WARN] {} is already deployed. Skipping".format(resource))
        pass
    else:
        print("[ERROR] could not deploy")
        raise e


def yamlParser(body, find_namespace=False):
    group, version = body["apiVersion"].split("/")
    plural = body["kind"].lower() + "s"
    if find_namespace:
        namespace = body["metadata"]["namespace"]
        return body, group, namespace, plural, version
    else:
        return body, group, plural, version


class ArgoInstaller:

    def __init__(self):

        self.timeout = 120
        self.setKubeConfig()
        if not self.getConfirmation():
            print("[WARN] Quitting")
            sys.exit(0)
        self.v1 = client.CoreV1Api()
        self.apiClient = client.ApiClient()
        self.customObjectApi = client.CustomObjectsApi(self.apiClient)
        self.ns_argocd = "argocd"
        self.ns_argo_workflow = "argo"
        self.argo_workflow_deployment_file = "manifests/argo-workflow/deployment/argo_workflow_deploy.yaml"
        self.argo_cd_deployment_file = "manifests/argo-cd/argo_cd_deploy.yaml"
        self.argo_cd_template_file = "manifests/argo-cd/argo_cd_template.yaml"
        self.node_port_patch = {"spec": {"type": "NodePort"}}

    @staticmethod
    def setKubeConfig():
        dotenv.load_dotenv(".env")
        kubeconfig = os.getenv("KUBECONFIG")

        if not os.path.expanduser(kubeconfig):
            logging.error("config file cannot be found at {}".format(kubeconfig))
            sys.exit(1)
        config.load_kube_config(config_file=kubeconfig, context="docker-desktop")

    def getConfirmation(self):
        print("[INFO] Cluster Info:")
        print(config.list_kube_config_contexts())
        return self.query_yes_no(question="would you like to continue with the settings?")

    @staticmethod
    def query_yes_no(question):
        yes = {'yes', 'y'}
        no = {'no', 'n'}
        done = False
        while not done:
            choice = input("{} yes or no: ".format(question)).lower()
            if choice in yes:
                return True
            elif choice in no:
                return False
            else:
                print("Please respond by yes or no.")

    def createNamespace(self, namespace: str):
        try:
            body = client.V1Namespace()
            body.metadata = client.V1ObjectMeta(name=namespace)
            namespaces = [ns.metadata.name for ns in self.v1.list_namespace().items]
            if namespace not in namespaces:
                self.v1.create_namespace(body=body)
                print("[INFO] {} namespace is  created".format(namespace))
            else:
                print("[INFO] {} namespace is found will not be created".format(namespace))

        except Exception as e:
            print(e)

    def deployFromYaml(self, api_client: client, yml: str, label: str, **kwargs):
        try:
            utils.create_from_yaml(api_client, yaml_file=yml, **kwargs)

        except utils.FailToCreateError as e:
            skip_if_already_exists(e, resource=label.upper())

        watcher = watch.Watch()
        for event in watcher.stream(func=self.v1.list_namespaced_pod, namespace=self.ns_argocd, timeout_seconds=self.timeout):
            if event['object'].status.phase == "Running":
                watcher.stop()
        print(f"[INFO ] {label.upper()} is complete.")

    def deployNamespacedCRD(self, yml: str):
        for bodi in loadYaml(yml):
            body, group, namespace, plural, version = yamlParser(bodi, find_namespace=True)

            try:
                self.customObjectApi.create_namespaced_custom_object(group, version, namespace, plural, body)
                print(f"[INFO] {group}/{version} has been created")
            except client.ApiException as e:
                if json.loads(e.body)["reason"] == "AlreadyExists":
                    pass

    def deployPlainCRD(self, yml: str):
        for bodi in loadYaml(yml):

            body, group, plural, version = yamlParser(bodi, find_namespace=False)

            try:
                self.customObjectApi.create_cluster_custom_object(group, version, plural, body)
                print(f"[INFO] {group}/{version} has been created")
            except client.ApiException as e:
                if json.loads(e.body)["reason"] == "AlreadyExists":
                    pass

    def getNodePort(self, namespace: str, service_name: str):
        response = self.v1.list_namespaced_service(namespace=namespace, field_selector=f"metadata.name={service_name}")
        if service_name == "argo-server":
            print(str(response.items))
        return str(response.items[0].spec.ports[0].node_port)

    def getSecret(self, namespace: str, secret_name: str):
        secret = str(self.v1.read_namespaced_secret(name= secret_name, namespace=namespace).data).replace("\'", "\"")
        return str(base64.b64decode(json.loads(secret)["password"]))[2:-1]

    def argoCDCredentials(self):
        port = self.getNodePort(self.ns_argocd, "argocd-server")
        secret = self.getSecret(self.ns_argocd, secret_name="argocd-initial-admin-secret")
        userName = "admin"
        print (f"[INFO] ArgoCD UI is accessible at https://localhost:{port}")
        print (f"[INFO] ArgoCD UI is username is {userName}")
        print (f"[INFO] ArgoCD UI is password is {secret}")

    def argoWFCredentials(self):
        self.patchService(name="argo-server", namespace=self.ns_argo_workflow, body=self.node_port_patch)
        port = self.getNodePort(self.ns_argo_workflow, "argo-server")
        print (f"[INFO] ArgoWorkflow UI is accessible at https://localhost:{port}")


    def patchService(self, name: str, namespace: str, body: dict, **kwargs):
        try:

            self.v1.patch_namespaced_service(name, namespace, body=body, **kwargs)
            print(f"[INFO] {name.upper()} has been patched.")
        except client.ApiException as e:
            print(e)


    def main(self):
        self.createNamespace(namespace=self.ns_argocd)
        self.createNamespace(namespace=self.ns_argo_workflow)
        self.deployFromYaml(api_client=self.apiClient, yml=self.argo_cd_deployment_file, label="argo-cd",
                            namespace=self.ns_argocd)
        self.deployFromYaml(api_client=self.apiClient, yml=self.argo_workflow_deployment_file, namespace=self.ns_argo_workflow, label="argo-workflow")
        self.deployNamespacedCRD(yml=self.argo_cd_template_file)
        self.patchService("argocd-server", namespace=self.ns_argocd, body=self.node_port_patch)
        self.argoCDCredentials()
        self.argoWFCredentials()




if __name__ == "__main__":
    self = ArgoInstaller()
    ArgoInstaller.main(self)
