FROM bitnami/kubectl

USER root

WORKDIR /opt
COPY ${KUBECONFIG} ${HOME}.kube/


RUN apt update && \
    apt install -y git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    git clone https://github.com/yavuzkaymak/argo-demo.git && \
    chmod +x /opt/argo-demo/main.sh


USER 1001
ENTRYPOINT ["/opt/argo-demo/main.sh"]



