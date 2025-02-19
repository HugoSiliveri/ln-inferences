import requests
import json 
import sys

url = "https://jdm-api.demo.lirmm.fr"

def getNodeById(node_id):
    response = requests.get(f"{url}/v0/node_by_id/{node_id}", verify=False)
    response.raise_for_status()
    return response.json()

def getNodeByName(node_name):
    response = requests.get(f"{url}/v0/node_by_name/{node_name}", verify=False)
    response.raise_for_status()
    return response.json()

def getRefinementsByNodeName(node_name):
    response = requests.get(f"{url}/v0/refinements/{node_name}", verify=False)
    response.raise_for_status()
    return response.json()

def getNodesTypes():
    response = requests.get(f"{url}/v0/node_types/", verify=False)
    response.raise_for_status()
    return response.json()

def getRelationsFrom(node_name):
    response = requests.get(f"{url}/v0/relations/from/{node_name}", verify=False)
    response.raise_for_status()
    return response.json()

def getRelationsFromTo(node1_name, node2_name):
    response = requests.get(f"{url}/v0/relations/from/{node1_name}/to/{name2_name}", verify=False)
    response.raise_for_status()
    return response.json()

def getRelationsTo(node_name):
    response = requests.get(f"{url}/v0/relations/to/{node_name}", verify=False)
    response.raise_for_status()
    return response.json()

def getRelationsTypes():
    response = requests.get(f"{url}/v0/relations_types/", verify=False)
    response.raise_for_status()
    return response.json()

    

def main():
    try:
        argv = sys.argv[:1]
        if (argv.length == 3):

            node1_name = argv[0]
            relation = argv[1]
            node2_name = argv[2]

main()
    

