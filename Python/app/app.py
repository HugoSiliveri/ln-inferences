import math
import sys
import requests
import api
import utils

def strategic_resolution(node1, relation, node2, type_ids):
    """
        Effectue une inférence entre deux nœuds (node1, relation, node2) en utilisant une stratégie
        
        Arguments :
        node1 -- Nom du nœud de départ.
        relation -- Nom de la relation à tester.
        node2 -- Nom du nœud cible.
        type_ids -- Identifiant du type de la strategie
    """

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
            return [node1, relation, node2, best_reasoning, score]
            print(f"✅ Lien trouvé pour {node1} {relation} {node2} | Score : {max_score}")
            print(" & ".join(best_reasoning))
        else:
            return None
    else:
        return None





if __name__ == "__main__":
    try:
        argv = sys.argv[1:]

        if len(argv) == 3:
            node1, relation, node2 = argv

            relation_id = utils.get_id_by_name(relation)
            if relation_id is None:
                print(f"❌ Relation inconnue : {relation}")
            else:
                results = [
                    strategic_resolution(node1, relation, node2, 6), # deduction
                    strategic_resolution(node1, relation, node2, 8), # induction
                    strategic_resolution(node1, relation, node2, 5) # synonyme
                ]

                valid_results = [res for res in results if res]
                best_result = max(valid_results, key=lambda x: x[-1]) if valid_results else None

                if (best_result is None):
                    print("❌ Aucun lien trouvé.")
                else:
                    print(f"✅ Lien trouvé pour {best_result[0]} {best_result[1]} {best_result[2]} | Score : {best_result[4]}")
                    print(" & ".join(best_result[3]))
            
        else:
            print("Usage: script.py <node1_name> <relation> <node2_name>")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")
