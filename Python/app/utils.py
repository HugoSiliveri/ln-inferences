
import json
import sys
import api
import math
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

def get_score(relation_weight1, relation_weight2):
    if (relation_weight1 < 0) or (relation_weight2 < 0):
        score = -math.sqrt(abs(relation_weight1 * relation_weight2))
    else: 
        score = math.sqrt(abs(relation_weight1 * relation_weight2))
    return score

def parse_input(user_input):
    """
    Analyse l'entrée utilisateur pour extraire nodeA, relation et nodeB.
    - La relation commence toujours par 'r_'.
    - Tout ce qui est avant 'r_' est nodeA.
    - Tout ce qui est après 'r_' est nodeB.
    """
    parts = user_input.strip().split()
    
    # Trouver l'index de la relation (le premier élément qui commence par "r_")
    relation_index = next((i for i, part in enumerate(parts) if part.startswith("r_")), None)

    if relation_index is None or relation_index == 0 or relation_index == len(parts) - 1:
        return None, None, None

    nodeA = " ".join(parts[:relation_index])
    relation = parts[relation_index]
    nodeB = " ".join(parts[relation_index + 1:])

    return nodeA, relation, nodeB
