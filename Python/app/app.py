import math
import sys
import requests
import api
import utils

def strategic_resolution(node1, relation_id, node2, type_ids):
    """
        Effectue une inférence entre deux nœuds (node1, relation, node2) en utilisant une stratégie.
        
        Arguments :
        node1 -- Nom du nœud de départ.
        relation_id -- Identifiant de la relation à tester.
        node2 -- Nom du nœud cible.
        type_ids -- Identifiant du type de la stratégie.
    """

    parameters1 = {'types_ids': str(type_ids)}
    nodes_of_node1 = api.get_relations_from(node1, parameters1)

    parameters2 = {'type_ids': str(relation_id)}
    result = api.get_relations_to(node2, parameters2)

    inferences = []

    if "relations" in result and result["relations"]:
        for relation_data in result["relations"]:
            if relation_data["type"] == relation_id:
                source_node = relation_data["node1"]

                for generic_node in nodes_of_node1["relations"]:
                    generic_node_id = generic_node["node2"]

                    if generic_node_id == source_node:
                        relation_weight2 = generic_node["w"]
                        relation_weight1 = relation_data["w"]  

                        if (relation_weight1 < 0) or (relation_weight2 < 0):
                            score = -math.sqrt(abs(relation_weight1 * relation_weight2))
                        else: 
                            score = math.sqrt(abs(relation_weight1 * relation_weight2))

                        type_name = utils.get_relation_name_by_id(type_ids)
                        relation_name = utils.get_relation_name_by_id(relation_id)
                        explanation = f"{node1} {type_name} ({relation_weight1}) {utils.get_node_name_by_id(generic_node_id)} & {utils.get_node_name_by_id(generic_node_id)} {relation_name} ({relation_weight2}) {node2}"
                        
                        inferences.append((explanation, score))

    return inferences


if __name__ == "__main__":
    try:
        argv = sys.argv[1:]

        if len(argv) == 3:
            node1, relation, node2 = argv

            relation_id = utils.get_relation_id_by_name(relation)
            if relation_id is None:
                print(f"❌ Relation inconnue : {relation}")
            else:
                results = []
                results.extend(strategic_resolution(node1, relation_id, node2, 6))  # Déduction
                results.extend(strategic_resolution(node1, relation_id, node2, 8))  # Induction
                results.extend(strategic_resolution(node1, relation_id, node2, 5))  # Synonyme
                results.extend(strategic_resolution(node1, relation_id, node2, relation_id)) # Transitivité

                # On trie par score décroissant et prendre les 10 meilleurs
                results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

                if not results:
                    print("❌ Aucun lien trouvé.")
                else:
                    max_score = results[0][1] if results else 1  # On évite une division par zéro
                    normalized_results = [(exp, score / max_score) for exp, score in results]

                    for i, (explanation, score) in enumerate(normalized_results, start=1):
                        print(f"{i} | oui | {explanation} | {round(score, 2)}")
        
        else:
            print("Usage: script.py <node1_name> <relation> <node2_name>")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")