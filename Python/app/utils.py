
import json
import sys
import api
import math

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

def get_score(relation_weight1, relation_weight2):
    if (relation_weight1 < 0) or (relation_weight2 < 0):
        score = -math.sqrt(abs(relation_weight1 * relation_weight2))
    else: 
        score = math.sqrt(abs(relation_weight1 * relation_weight2))
    return score
