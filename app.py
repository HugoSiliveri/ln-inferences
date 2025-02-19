import requests
import json
import sys
import math

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

def get_id_by_name(search_name):
    with open('relations.json', 'r') as file:
        data = json.load(file)
        
    for entry in data:
        if entry['nom'] == search_name:
            return entry['id']
    return None

def get_node_name_by_id(node_id):
    node = get_node_by_id(node_id)
    return node['name']


def strategie_deduction(node1, relation, node2):
    """
        Effectue une déduction entre trois nœuds (node1, relation, node2) 
        en utilisant des relations génériques et vérifie si une relation spécifique existe entre node1 et node2.
        
        Arguments :
        node1 -- Nom du nœud de départ.
        relation -- Nom de la relation à tester.
        node2 -- Nom du nœud cible.
    """
    relation_id = get_id_by_name(relation)
    if relation_id is None:
        print(f"❌ Relation inconnue : {relation}")
        return None

    parameters1 = {'types_ids': '6'}
    generics_of_node1 = get_relations_from(node1, parameters1)

    parameters2 = {'type_ids': str(relation_id)}
    result = get_relations_to(node2)

    W = []
    max_score = -float('inf')
    best_reasoning = []

    if "relations" in result and result["relations"]:
        for relation_data in result["relations"]:
            if relation_data["type"] == relation_id:
                source_node = relation_data["node1"]

                for generic_node in generics_of_node1["relations"]:
                    generic_node_id = generic_node["node2"]

                    if generic_node_id == source_node:
                        relation_weight_generic = generic_node["w"]
                        relation_weight_current = relation_data["w"]  

                        if relation_weight_generic < 0 or relation_weight_current < 0:
                            continue

                        score = math.sqrt(relation_weight_generic * relation_weight_current)
                        if score > max_score:
                            max_score = score
                            reasoning_steps = [
                                f"{node1} r-isa {get_node_name_by_id(generic_node_id)}",
                                f"{get_node_name_by_id(generic_node_id)} {relation} {node2}"
                            ]
                            best_reasoning = reasoning_steps

        if best_reasoning:
            print(f"✅ Lien trouvé pour {node1} {relation} {node2}")
            print(" & ".join(best_reasoning))
        else:
            print("❌ Aucun lien trouvé.")
    else:
        print(f"❌ Aucun lien trouvé pour {node2}.")

if __name__ == "__main__":
    try:
        argv = sys.argv[1:]
        if len(argv) == 3:
            node1, relation, node2 = argv
            strategie_deduction(node1, relation, node2)
        else:
            print("Usage: script.py <node1_name> <relation> <node2_name>")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")
