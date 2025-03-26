import requests
import api
import utils
from itertools import chain

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

    # Récupération des relations
    nodes_of_nodeA = api.get_relations_from(nodeA, {'types_ids': str(type_ids)})  # A -R1-> C
    result = api.get_relations_to(nodeB, {'type_ids': str(relationR_id)})  # C -R-> B

    if not nodes_of_nodeA.get("relations") or not result.get("relations"):
        return []

    # Normalisation des poids
    max_weight1 = max((rel["w"] for rel in result["relations"] if rel["type"] == relationR_id), default=1)
    max_weight2 = max((rel["w"] for rel in nodes_of_nodeA["relations"]), default=1)

    # Création d'un set pour une recherche rapide
    nodesC_from_B = {rel["node1"]: rel["w"] for rel in result["relations"] if rel["type"] == relationR_id}

    inferences = []

    for relationR_data in nodes_of_nodeA["relations"]:
        nodeC_id = relationR_data["node2"]
        if nodeC_id in nodesC_from_B:
            # Récupérer les poids normalisés
            relation_weight1 = nodesC_from_B[nodeC_id] / max_weight1
            relation_weight2 = relationR_data["w"] / max_weight2
            score = utils.get_score(relation_weight1, relation_weight2)

            nodeC_name = utils.get_node_name_by_id(nodeC_id)
            explanation = f"{nodeA} {utils.get_relation_name_by_id(type_ids)} ({relation_weight1:.2f}) {nodeC_name} & {nodeC_name} {utils.get_relation_name_by_id(relationR_id)} ({relation_weight2:.2f}) {nodeB}"

            inferences.append((explanation, score))

    return inferences


if __name__ == "__main__":
    try:
        while True:
            user_input = input("Entrez '<nodeA> <relation> <nodeB>' (ou 'exit' pour quitter) : ").strip()
            
            if user_input.lower() == "exit":
                break
            
            nodeA, relation, nodeB = utils.parse_input(user_input)

            if not nodeA or not relation or not nodeB:
                print("Format invalide \n")
                continue

            relationR_id = utils.get_relation_id_by_name(relation)
            if relationR_id is None:
                print(f"Relation inconnue : {relation}\n")
                continue

            type_ids_list = [6, 8, 5, relationR_id]  # Déduction, Induction, Synonyme, Transitivité
            results = list(chain.from_iterable(
                strategic_resolution(nodeA, relationR_id, nodeB, type_id) for type_id in type_ids_list
            ))

            # Trier et prendre les 10 meilleurs
            results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

            if not results:
                print("Aucun lien trouvé.\n")
            else:
                for i, (explanation, score) in enumerate(results, start=1):
                    print(f"{i} | oui | {explanation} | {round(score, 4)}")
                print("\n")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")
    except KeyboardInterrupt:
        print("\nProgramme interrompu.")