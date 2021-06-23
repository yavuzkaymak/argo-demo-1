import logging
import os
import sys
import urllib.request

from kubernetes import client, config, watch, utils
import dotenv
import yaml


def loadYaml(link: str):
    try:
        with urllib.request.urlopen(link) as f:
            file = f.read().decode('utf-8')
            print(file)
        return yaml.load(file)
    except yaml.YAMLError as e:
        print("[ERROR] could not down file at {}".format(link))
        print("[ERROR]  {}".format(e))


# noinspection PyBroadException
def skip_if_already_exists(e, resource: str):
    import json
    info = json.loads(e.api_exceptions[0].body)
    if info.get('reason').lower() == 'alreadyexists':
        print("[WARN] {} is already deployed. Skipping".format(resource))
        pass
    else:
        print("[ERROR] could not deploy")
        raise e


class ArgoInstaller:

    def __init__(self):

        self.timeout = 120
        self.setKubeConfig()
        if not self.getConfirmation():
            print("[WARN] Quitting")
            sys.exit(0)
        self.v1 = client.CoreV1Api()
        self.apiClient = client.ApiClient()
        self.ns = None
        self.argo_workflow_deployment_file = "manifests/argo-workflow/deployment/argo_workflow_deploy.yaml"
        self.argo_cd_deployment_file = "manifests/argo-cd/argo_cd_deploy.yaml"

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
            self.ns = namespace
        except Exception as e:
            print(e)

    def deployFromYaml(self, api_client: client.ApiClient, yml: str, label: str):
        try:
            utils.create_from_yaml(api_client, yaml_file=yml, namespace=self.ns)

        except utils.FailToCreateError as e:
            skip_if_already_exists(e, resource=yml)

        watcher = watch.Watch()
        for event in watcher.stream(func=self.v1.list_namespaced_pod, namespace=self.ns, timeout_seconds=self.timeout):
               if event['object'].status.phase == "Running":
                watcher.stop()
        print("no more waiting")



    def main(self):
        self.createNamespace(namespace="argo-cd")
        self.deployFromYaml(api_client=self.apiClient, yml=self.argo_cd_deployment_file,label="argo-cd")


if __name__ == "__main__":
    self = ArgoInstaller()
    ArgoInstaller.main(self)
