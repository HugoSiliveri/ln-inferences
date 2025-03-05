import requests
import json

requests.packages.urllib3.disable_warnings() 
url = "https://jdm-api.demo.lirmm.fr"

############### ROUTES API ###############

def get_node_by_id(node_id):
    response = requests.get(f"{url}/v0/node_by_id/{node_id}", verify=False)
    response.raise_for_status()
    return response.json()

def get_node_by_name(node_name):
    response = requests.get(f"{url}/v0/node_by_name/{node_name}", verify=False)
    response.raise_for_status()
    return response.json()

def get_relations_from(node_name, parameters):
    response = requests.get(f"{url}/v0/relations/from/{node_name}", params=parameters, verify=False)
    response.raise_for_status()
    return response.json()

def get_relations_from_to(node1_name, node2_name, parameters):
    response = requests.get(f"{url}/v0/relations/from/{node1_name}/to/{node2_name}", params=parameters, verify=False)
    response.raise_for_status()
    return response.json()

def get_relations_to(node_name):
    response = requests.get(f"{url}/v0/relations/to/{node_name}", verify=False)
    response.raise_for_status()
    return response.json()

#########################################