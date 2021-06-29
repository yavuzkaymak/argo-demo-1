FROM bitnami/kubectl

USER root

WORKDIR /opt
COPY ${KUBECONFIG} ${HOME}.kube/
COPY contrib/entrypoint.sh ./contrib/


RUN apt update && \
    apt install -y git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

USER 1001
ENTRYPOINT ["/opt/contrib/entrypoint.sh"]



