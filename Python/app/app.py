import math
import sys
import requests
import api
import utils

def strategic_resolution(nodeA, relationR_id, nodeB, type_ids):
    """
        Effectue une inférence entre deux nœuds (nodeA, relationR, nodeB) en utilisant une stratégie.
        
        Arguments :
        nodeA -- Nom du nœud de départ.
        relationR_id -- Identifiant de la relation à tester.
        nodeB -- Nom du nœud cible.
        type_ids -- Identifiant du type de la stratégie.

        Triangle : 
                C
            R1     R
        A       R       B
    """

    parameters1 = {'types_ids': str(type_ids)}
    nodes_of_nodeA = api.get_relations_from(nodeA, parameters1)  # Les noeuds C dans la relation A -R1- C

    parameters2 = {'type_ids': str(relationR_id)}
    result = api.get_relations_to(nodeB, parameters2)  # Les noeuds C dans la relation C -R- B

    inferences = []

    if "relations" in result and result["relations"]:
        # Trouver les poids max pour normalisation
        max_weight1 = max((rel["w"] for rel in result["relations"] if rel["type"] == relationR_id), default=1)
        max_weight2 = max((rel["w"] for rel in nodes_of_nodeA["relations"]), default=1)

        for relationR1_data in result["relations"]:
            if relationR1_data["type"] == relationR_id:
                nodeCFromA_id = relationR1_data["node1"]

                for relationR_data in nodes_of_nodeA["relations"]:
                    nodeCToB_id = relationR_data["node2"]

                    if nodeCToB_id == nodeCFromA_id:
                        # Normalisation des poids
                        relation_weight1 = relationR1_data["w"] / max_weight1
                        relation_weight2 = relationR_data["w"] / max_weight2
                        score = utils.get_score(relation_weight1, relation_weight2)

                        type_name = utils.get_relation_name_by_id(type_ids)
                        relation_name = utils.get_relation_name_by_id(relationR_id)
                        explanation = f"{nodeA} {type_name} ({relation_weight1:.2f}) {utils.get_node_name_by_id(nodeCToB_id)} & {utils.get_node_name_by_id(nodeCToB_id)} {relation_name} ({relation_weight2:.2f}) {nodeB}"
                        
                        inferences.append((explanation, score))

    return inferences


if __name__ == "__main__":
    try:
        argv = sys.argv[1:]

        if len(argv) == 3:
            nodeA, relation, nodeB = argv

            relationR_id = utils.get_relation_id_by_name(relation)
            if relationR_id is None:
                print(f"❌ Relation inconnue : {relation}")
            else:
                results = []
                results.extend(strategic_resolution(nodeA, relationR_id, nodeB, 6))  # Déduction
                results.extend(strategic_resolution(nodeA, relationR_id, nodeB, 8))  # Induction
                results.extend(strategic_resolution(nodeA, relationR_id, nodeB, 5))  # Synonyme
                results.extend(strategic_resolution(nodeA, relationR_id, nodeB, relationR_id))  # Transitivité

                # On trie par score décroissant et prend les 10 meilleurs
                results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

                if not results:
                    print("❌ Aucun lien trouvé.")
                else:
                    for i, (explanation, score) in enumerate(results, start=1):
                        print(f"{i} | oui | {explanation} | {round(score, 4)}")
        
        else:
            print("Usage: script.py <nodeA_name> <relation> <nodeB_name>")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")