import requests
import sys
from pathlib import Path
from itertools import chain

sys.path.append(str(Path(__file__).resolve().parent.parent))
import api
import utils

def levenshtein_distance(a, b): #code d'origine https://dev.to/jmegnidro/distance-de-levenshtein-le-guide-ultime-pour-mesurer-la-similarite-textuelle-3m7f
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[n][m]

def hasCommonAnnotation(liste1,liste2):
    for e1 in liste1:
        for e2 in liste2:
            lv = levenshtein_distance(e1,e2)
            if(lv < 2):
                return True
    return False


def strategic_resolution(nodeA, relationR_id, nodeB, type_ids, acceptedAnnotations):
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
    try :
        # Récupération des relations
        nodes_of_nodeA = api.get_relations_from(nodeA, {'types_ids': str(type_ids),'min_weight': str(1)})  # A -R1-> C
        result = api.get_relations_to(nodeB, {'type_ids': str(relationR_id),'min_weight': str(1)})  # C -R-> B
    except requests.exceptions.RequestException as e:
        return  []


    # Normalisation des poids
    try :
        max_weight1 = max((rel["w"] for rel in result["relations"] if rel["type"] == relationR_id), default=1)
        max_weight2 = max((rel["w"] for rel in nodes_of_nodeA["relations"]), default=1)
    except KeyError:
        return  []

    # Création d'un dictionnaire pour une recherche rapide
    nodesC_from_B = {rel["node1"]: [rel["w"], rel["id"]] for rel in result["relations"] if rel["type"] == relationR_id}

    inferences = []
    

    for relationR_data in nodes_of_nodeA["relations"]:
        nodeC_id = relationR_data["node2"]
        if nodeC_id in nodesC_from_B:
            #On récupère les annotations de la première prémisse
            try :
                annotations_premisse1 = api.get_relations_from(":r"+str(relationR_data["id"]), {'types_ids': str(998)})
            except requests.exceptions.RequestException as e:
                annotations1_names = []
            else:
                try :
                    annotations1_names = [e["name"] for e in annotations_premisse1["nodes"]]
                    annotations1_names.pop(annotations1_names.index(":r"+str(relationR_data["id"])))
                except KeyError:
                    annotations1_names = []
            if not("contrastif" in annotations1_names):# Test d'existance de l'annotation contrastif sur P1
                #Si la premisse est contrastive ca ne sert a rien de chercher les raffinnements du mots qui sont en relation avec A, ils sont dejà dans la liste nodes_ofnoeA["relations"]
                try :
                    annotations_premisse2 = api.get_relations_from(":r"+str(nodesC_from_B[nodeC_id][1]), {'types_ids': str(998)})
                except requests.exceptions.RequestException as e:
                    annotations2_names = []
                else :
                    try :
                        annotations2_names = [e["name"] for e in annotations_premisse2["nodes"]]
                        annotations2_names.pop(annotations2_names.index(":r"+str(nodesC_from_B[nodeC_id][1])))
                    except KeyError :
                        annotations2_names = []
                        print("le dico renvoyer par la requête https://jdm-api.demo.lirmm.fr/v0/relations/from/"+str(nodesC_from_B[nodeC_id][1])+"?types_ids=998 a eu un format inattendu")
                if not("contrastif" in annotations2_names):#On teste si P2 est contrastif
                    # Récupérer les poids normalisés
                    relation_weight1 = nodesC_from_B[nodeC_id][0] / max_weight1
                    relation_weight2 = relationR_data["w"] / max_weight2
                    score = utils.get_score(relation_weight1, relation_weight2)
        
                    nodeC_name = utils.get_node_name_by_id(nodeC_id)
                    explanation = f"{nodeA} {utils.get_relation_name_by_id(type_ids)} ({relation_weight1:.2f}) {nodeC_name} & {nodeC_name} {utils.get_relation_name_by_id(relationR_id)} ({relation_weight2:.2f}) {nodeB}"
        
                    allAnotations = annotations1_names
                    for e in annotations2_names:
                        if(not(e in allAnotations)):
                            allAnotations.append(e)
                    if(acceptedAnnotations == [""] or hasCommonAnnotation(allAnotations,acceptedAnnotations)):
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
                print("Format invalide\n")
                continue

            relationR_id = utils.get_relation_id_by_name(relation)
            if relationR_id is None:
                print(f"Relation inconnue : {relation}\n")
                continue

            # Définir les stratégies disponibles
            strategies = {
                "Déduction": 6,
                "Induction": 8,
                "Synonyme": 5,
                "Transitivité": relationR_id
            }

            # Demander à l'utilisateur de choisir les stratégies
            print("Choisissez les stratégies à utiliser (1 = oui, 0 = non) :")
            chosen_flags = []
            for name in strategies:
                while True:
                    choice = input(f"Utiliser la stratégie '{name}' ? (1/0) : ").strip()
                    if choice in ["0", "1"]:
                        chosen_flags.append(int(choice))
                        break
                    else:
                        print("Veuillez entrer 1 (oui) ou 0 (non).")

            # Construire la liste filtrée
            type_ids_list = [strategy_id for (flag, (_, strategy_id)) in zip(chosen_flags, strategies.items()) if flag == 1]

            if not type_ids_list:
                print("Aucune stratégie sélectionnée.\n")
                continue

            liste = input(f"Entrez une liste des annotations à inspecter (séprarées par des points virgules), si vide renvoie toutes les relations trouvées : ").strip()
            liste = liste.split(";")

            results = list(chain.from_iterable(
                strategic_resolution(nodeA, relationR_id, nodeB, type_id, liste) for type_id in type_ids_list
            ))

            results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

            if not results:
                print("Aucun lien trouvé.\n")
            else:
                cpt = 0
                for i, (explanation, score) in enumerate(results, start=1):
                    print(f"{i} | oui | {explanation} | {round(score, 4)}")
                print("\n")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau : {e}")
    except KeyboardInterrupt:
        print("\nProgramme interrompu.")