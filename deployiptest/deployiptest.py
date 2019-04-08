#!/usr/local/env python3

import argparse
import sys
from pprint import pprint
from pathlib import Path
from kubernetes import client, config


def loadConfig(kubeconfig=None):
    if kubeconfig:
        my_file = Path(kubeconfig)
        if my_file.is_file():
            print("Using kubeconfig: ", kubeconfig)
            config.load_kube_config(config_file=kubeconfig)
        else:
            print("Kubeconfig could not be loaded")
            sys.exit(1)
    else:
        print("Using default config")
        config.load_kube_config()

def getDeployments():
    k8s_beta = client.ExtensionsV1beta1Api()
    deployments = {}
    deployments_items = k8s_beta.list_deployment_for_all_namespaces().items
    for deployment in deployments_items:
        namespace = deployment.metadata.namespace
        name = deployment.metadata.name
        if namespace not in deployments:
            deployments[namespace] = {}
        if name not in deployments[namespace]:
            deployments[namespace][name] = deployment.spec.selector.match_labels
    return deployments


def getServiceIPsForDeployments(deployments):
    v1 = client.CoreV1Api()
    serviceIPList = []
    for namespace in deployments.keys():
        ret = v1.list_namespaced_service(namespace)
        for service in ret.items:
            if service.spec.type == 'LoadBalancer':
                for deployment_name, deployment_value in deployments[namespace].items():
                    if service.spec.selector == deployment_value:
                        value = {'namespace': namespace, 'deployment_name': deployment_name, 'ip': service.status.load_balancer.ingress[0].ip}
                        value['ports'] = [{'port': port.port, 'protocol': port.protocol} for port in service.spec.ports]
                        serviceIPList.append(value)
    return serviceIPList


def testEndpoints(serviceIPList):
    import requests
    for serviceIPDict in serviceIPList:
        for portDict in serviceIPDict['ports']:
            if portDict['protocol'] == 'TCP':
                urlProtocol = "http"
                r = None
                requestFunc = None

                if portDict['port'] in (443, 8443):
                    urlProtocol = "https"
                    url = "%s://%s:%d/" % (urlProtocol, serviceIPDict['ip'], portDict['port'])
                    requestFunc = lambda url : requests.get(url, verify=False)
                else:
                    url = "%s://%s:%d/" % (urlProtocol, serviceIPDict['ip'], portDict['port'])
                    requestFunc = lambda url : requests.get(url)

                print("Attempting to access service for deployment", serviceIPDict['deployment_name'], "in namespace", serviceIPDict['namespace'], ':', url)
                r = requestFunc(url)

                if r.status_code == 200:
                    print("Connection succeded!\n")
                else:
                    print("Received status code: ", r.status_code, "\n")

            else:
                print("Unsupported protocol: ", portDict['protocol'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="path to kubeconfig")
    args = parser.parse_args()

    loadConfig(args.config)
    deployments = getDeployments()

    serviceIPList = getServiceIPsForDeployments(deployments)
    pprint(serviceIPList)
    testEndpoints(serviceIPList)

if __name__ == "__main__":
    main()
    sys.exit(0)