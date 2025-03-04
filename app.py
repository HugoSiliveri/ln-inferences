import math
import sys
import requests
import api
import utils

def strategic_resolution(node1, relation, node2, type_ids):
    """
        Effectue une resolution logique entre trois nœuds (node1, relation, node2) 
        en utilisant une stratégie et vérifie si une relation spécifique existe entre node1 et node2.
        
        Arguments :
        node1 -- Nom du nœud de départ.
        relation -- Nom de la relation à tester.
        node2 -- Nom du nœud cible.
        type_ids -- Identifiant du type de la strategie
    """
    relation_id = utils.get_id_by_name(relation)
    if relation_id is None:
        print(f"❌ Relation inconnue : {relation}")
        return None

    parameters1 = {'types_ids': str(type_ids)}
    nodes_of_node1 = api.get_relations_from(node1, parameters1)

    parameters2 = {'type_ids': str(relation_id)}
    result = api.get_relations_to(node2)

    W = []
    max_score = -float('inf')
    best_reasoning = []

    if "relations" in result and result["relations"]:
        for relation_data in result["relations"]:
            if relation_data["type"] == relation_id:
                source_node = relation_data["node1"]

                for generic_node in nodes_of_node1["relations"]:
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
                                f"{node1} r-isa {utils.get_node_name_by_id(generic_node_id)}",
                                f"{utils.get_node_name_by_id(generic_node_id)} {relation} {node2}"
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

        if len(argv) == 4:
            node1, relation, node2, strategy = argv
            type_ids = -1

            match strategy:
                case "deduction":
                    strategic_resolution(node1, relation, node2, 6)
                case "induction":
                    strategic_resolution(node1, relation, node2, 8)
                case "synonyme":
                    strategic_resolution(node1, relation, node2, 6)
                case _: 
                    print("Stratégie inconnue")
            
        else:
            print("Usage: script.py <node1_name> <relation> <node2_name> <strategy>")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")
