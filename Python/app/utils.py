
import json
import sys
import api

def get_relation_id_by_name(name):
    with open('relations.json', 'r') as file:
        data = json.load(file)
        
    for entry in data:
        if entry['nom'] == name:
            return entry['id']
    return None

def get_relation_name_by_id(id):
    with open('relations.json', 'r') as file:
        data = json.load(file)
        
    for entry in data:
        if entry['id'] == id:
            return entry['nom']
    return None



def get_node_name_by_id(node_id):
    node = api.get_node_by_id(node_id)
    return node['name']
