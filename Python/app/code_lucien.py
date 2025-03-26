import requests
import json
from math import *

url = "https://jdm-api.demo.lirmm.fr/v0/"

def relationDepuisUnNoeud(node,relationid):
    req = url+"relations/from/"+node+"?types_ids="+str(relationid)+"&min_weight=1"
    print(req)
    r = requests.get(req)
    return r.json()


#https://jdm-api.demo.lirmm.fr/v0/relations/to/{node2_name}
def relationVersUnNoeud(node,relationid):
    req = url+"relations/to/"+node+"?types_ids="+str(relationid)+"&min_weight=1"
    print(req)
    return requests.get(req).json()

#https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}
def noeudParId(nodeid):
    req = url+"node_by_id/"+str(nodeid)
    return requests.get(req).json()

#https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}
def relationFromNoeudToNoeud(node1,relationId,node2):
    req = url+"/relations/from/"+node1+"/to/"+node2+"?types_ids="+str(relationId)
    print(req)
    return requests.get(req).json()

#https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}
def noeudParNom(nodeName):
    req = url+"node_by_name/"+nodeName
    print(req)
    return requests.get(req).json()


def TriGéométrique(e): #Autres possibilités de tris, affinner en privilégiant des mots fréquent ou des mots plus précis scientifiquement ("exemple colombidé pour savoir si un animal a des ailes")
    w = e[1]["d1"]["weight"] * e[1]["d2"]["weight"]
    if(w < 0):
        w = (-1) * sqrt(w*(-1))
    else :
        w = sqrt(w)
    return w


#Cette fonction permet de formater les données pour les rendre plus facile a manipuler dans la suite des fonctions de recherche
#Actuellement cette fonction prend en charge la recherche de doublont ou de valeurs manquantes dans les réponses de l'API, c'est une opération trés lourde que je compte
#déplacer dans le futur est ne pas exécuter sur chaque entrée (filtrage à l'aide des valeurs de #relations et #nodes)
def MakeDico(request):
    try :
        request["request"]["node1"]
            #dir est une variable qui donne la direction de la relation demandée, il vaut 1 si les relations partent du noeud commun 2 si c'est l'inverse
        dir = 1
    except KeyError:
        try :
            request["request"]["node2"]
            dir = 2
        except KeyError:
            #Ca c'est un cas totalement improbable mais je l'ai quand même mis au cas ou, la valeur de retour dans ce cas ests pourrie j'en ai bien conscience mais flemme, de toute façon c'est pas cénsé arriver
            print("Error ! ni node1 ni node 2 ne sont présent dans le champ request de la requête")
            return {}
    dico ={}
    nbRel = request["request"]["#relations"]
    nbNodes = request["request"]["#nodes"]
    print("Pour : "+str(request["request"]["node"+str(dir)]) +" nb lignes a traiter : "+str(nbRel) + " , nombre de noeuds : "+str(nbNodes))
    Inexistant = []
    existants = []
    dico = {}
    doubles = []
    for i in range(request["request"]["#relations"]):
        id1 = request["relations"][i]["node"+str(dir%2+1)]
        if(id1 not in existants):#si l'id du noeud présent dans le tuples du champ relations actuellement inspéctés n'a pas déja été vu 
            existants.append(id1)
            found = False
            for j in range(request["request"]["#nodes"]):
                if(id1 == request["nodes"][j]["id"]):#içi on cherche si l'id est présent dans le champ nodes de la requêtes qui permet de récupérer le nom
                    found = True
                    d={"weight" : request["relations"][i]["w"] , "name" : request["nodes"][j]["name"] , "node_weight" : request["nodes"][j]["w"]}
                    dico.update({request["nodes"][j]["id"] : d})#içi on construit le nouveau dico 
                    break
        else :
            doubles.append(id1)
        if(not found):
            Inexistant.append(request["relations"][i]["node"+str(dir%2+1)])
    #On affiche les doublons et les inexistan,ts mais on ne les renvoie pas parceque j'y ai pas vus d'interêt, ça peut changer si tu veux
    print("Inexistant dans le champ nodes : "+str(Inexistant)+" , Présents en double dans les requêtes : "+str(doubles))
    return dico

def Deduction(node1,relationId,node2):
    generiques1 = relationDepuisUnNoeud(node1,6)
    vEntrantRel = relationVersUnNoeud(node2,relationId)
    n1 = generiques1["request"]["#relations"]
    try:
        n2 = vEntrantRel["request"]["#relations"]
    except KeyError:
        print("nous n'avons trouver aucune information sur la relation demandée")
        return "Error : keyError"
    #On crée les nouveau dicos dont le format devrait permettre une recherche plus rapide (j'ai pas fait le calcul)
    d1 = MakeDico(generiques1)
    d2 = MakeDico(vEntrantRel)
    interId = list(set(d1.keys()).intersection(d2.keys()))#calcul de l'intersection
    if(len(interId) == 0):
        print("nous n'avons trouver aucune information sur la relation demandée")
        print("intersection vide")
        return {}
    print("taille intersection : "+ str(len(interId)))
    intersection = {}
    for i in range(len(interId)):#Içi on crée un nouveau format de dico (oui encore) pour préparer le calcul des poids dérivations
        intersection.update({ interId[i] : { "d1" : d1[interId[i]] , "d2" : d2[interId[i]]}})
    intersection = sorted(intersection.items(), key=TriGéométrique, reverse=True)#tri des résulats via leur poid cumulé
    #le format change aprés l'appel a la fonction sorted
    #nouveau format intersection : [(idNoeudIntermédiaire, {'d1': d1[idNoeudIntermédiaire], 'd2': d2[idNoeudIntermédiaire]})]
    for i in range(len(interId)):#affichage
        print(str(i) + " | "+intersection[i][1]["d1"]["name"]+" | poids 1 : "+str(intersection[i][1]["d1"]["weight"])+" | poids 2 : "+str(intersection[i][1]["d2"]["weight"]))
    return intersection



#Utiliser les Induction pui les synonymes (deux stratégies différentes)

def Induction(node1,relationId,node2):
    generiques1 = relationDepuisUnNoeud(node1,8)#Les fonctions suivantes sont a peu prés les mêmes seul la relation utiliser içi (dans ce cas 8) change
    vEntrantRel = relationVersUnNoeud(node2,relationId)
    n1 = generiques1["request"]["#relations"]
    try:
        n2 = vEntrantRel["request"]["#relations"]
    except KeyError:
        print("nous n'avons trouver aucune information sur la relation demandée")
        return "Error : keyError"
    d1 = MakeDico(generiques1)
    d2 = MakeDico(vEntrantRel)
    interId = list(set(d1.keys()).intersection(d2.keys()))#calcul de l'intersection
    if(len(interId) == 0):
        print("nous n'avons trouver aucune information sur la relation demandée")
        print("intersection vide")
        return {}
    print("taille intersection : "+ str(len(interId)))
    intersection = {}
    for i in range(len(interId)):
        intersection.update({ interId[i] : { "d1" : d1[interId[i]] , "d2" : d2[interId[i]]}})
    intersection = sorted(intersection.items(), key=TriGéométrique, reverse=True)#tri des résulats via leur poid cumulé
    #format intersection : [(idNoeudIntermédiaire, {'d1': d1[idNoeudIntermédiaire], 'd2': d2[idNoeudIntermédiaire]})]
    for i in range(len(interId)):#affichage
        print(str(i) + " | "+intersection[i][1]["d1"]["name"]+" | poids 1 : "+str(intersection[i][1]["d1"]["weight"])+" | poids 2 : "+str(intersection[i][1]["d2"]["weight"]))
    return intersection

def Synonymes(node1,relationId,node2):
    generiques1 = relationDepuisUnNoeud(node1,5)#rajouter poid min 1 
    vEntrantRel = relationVersUnNoeud(node2,relationId)
    n1 = generiques1["request"]["#relations"]
    try:
        n2 = vEntrantRel["request"]["#relations"]
    except KeyError:
        print("nous n'avons trouver aucune information sur la relation demandée")
        return "Error : keyError"
    d1 = MakeDico(generiques1)
    d2 = MakeDico(vEntrantRel)
    interId = list(set(d1.keys()).intersection(d2.keys()))#calcul de l'intersection
    if(len(interId) == 0):
        print("nous n'avons trouver aucune information sur la relation demandée")
        print("intersection vide")
        return {}
    print("taille intersection : "+ str(len(interId)))
    intersection = {}
    for i in range(len(interId)):
        intersection.update( {interId[i] : { "d1" : d1[interId[i]] , "d2" : d2[interId[i]]}}) #Ajout au dictionnaire des résultats et choix d format de celui-ci
    intersection = sorted(intersection.items(), key=TriGéométrique, reverse=True)#tri des résulats via leur poid cumulé
    #format intersection : [(idNoeudIntermédiaire, {'d1': d1[idNoeudIntermédiaire], 'd2': d2[idNoeudIntermédiaire]})]
        #for i in range(len(interId)):#affichage
        #    print(str(i) + " | "+intersection[i][1]["d1"]["name"]+" | poids 1 : "+str(intersection[i][1]["d1"]["weight"])+" | poids 2 : "+str(intersection[i][1]["d2"]["weight"]))
    return intersection


#Cette fonction permet de récupérer les id des relations à partir de leur nom en utilisant le beau dico d'Hugo
def getIdRel(nom):
    try :
        with open("relations.json") as f :
            data = json.load(f)
    except JSONDecodeError :
        print("hugo il a fait des bétises son fichier il est pourri")
        return -1
    for i in range(len(data)):
        if(nom == data[i]["nom"]):#on cherche le nom de la relation dans le dico des relations 
            return data[i]["id"]
    print("la relation n'existe pas sous ce nom")#Si on trouve rien c'est que la relation a mal été écrite par l'utilisateur
    return -1

#Cette fonction permet d'effectuer une recherche directe, c'est a dire chercher qu'une relation d'un type précisé existe entre deux noeuds
def direct(node1,idRel,node2):
    request = relationFromNoeudToNoeud(node1,idRel,node2)
    print(request)
    try :
        if(request["request"]["#relations"] > 1):
            print("il y a plusieurs relations pour deux noeuds et un même type de relation, on renvoie la première")
        if(request["relations"][0]["w"] < 0):
            #si l'API a renvoie une relation avec un poids négatif, alors la relation est fausse, on renvoie donc un couple -1 + infos de la relation en question
            #le deuxième élément du couoke a le même format que les résultats des autres fonction de recherche, c'est pour facilité son traitement dans la fonction principale 
            return (-1,(-1 , { "d1" : {"weight" : request["relations"][0]["w"] , "name" : request["nodes"][0]["name"] , "node_weight" : request["nodes"][0]["w"]}}))
        else: 
            #Içi le poids de la relation est positif, ca veut dire qu'elle est vraie, donc on renvoie 1
            return (1,(-1 , { "d1" : {"weight" : request["relations"][0]["w"] , "name" : request["nodes"][0]["name"] , "node_weight" : request["nodes"][0]["w"]}}))
    except KeyError :
        #Içi on regarde si les nom des noeuds sont bien porthographiés, si oui alors il n'y a pas de relation qui corresponde a cette requête. 
        try :
            noeudParNom(node1)["name"]
            noeudParNom(node2)["name"]
        except KeyError :
            print("nom de noeuds mals orthographiés")
            return (0,"Error : Erreur de saisie")
        print("pas de relation directe")
        return (0,())#On renvoie un couple pour respecter le format de retour de la fonction, içi le 0 indique qu'on a rien trouvé
        
def printResult(dico):
    for i in range(len(dico)):#affichage
        try :
            print(str(i) + " | "+dico[i][1]["d1"]["name"]+" | poids 1 : "+str(dico[i][1]["d1"]["weight"])+" | poids 2 : "+str(dico[i][1]["d2"]["weight"]))
        except KeyError : #affichage si d2 n'est pas présent dans le dico c'est probablement que le résultat a été trouvé en une seule étape
            print(str(i) + " | "+dico[i][1]["d1"]["name"]+" | poids 1 : "+str(dico[i][1]["d1"]["weight"]))

def App(node1,relation,node2):#Une fonction plus facile a utiliser qui prend en entrée un triplet (mot1,relation,mot1) avec la relationsous forme de nom et pas d'id
    idRel = getIdRel(relation)
    if(idRel == -1): #si l'id est -1 alors c'est que la fonction getIdRel a rencontré un problème
        return -1
    print("l'id de la relation est "+str(idRel))

    #içi il faut choisir l'ordre des stratégies de recherche a employer et quand s'arrêter
    #Pour le moment j'ai choisi recherche directe, Déduction, Induction et Synonyme. Je m'arrête dés que j'ai un résultat. 

    result , dico = direct(node1,idRel,node2)
    if(result == -1):
        print("la relation est fausse")
        return False
    if(result == 1):
        print("il y a une solution, la voici")
        printResult([dico])
        return True
    if(result == 0):
        if (dico == "Error : Erreur de saisie"):
            return 0
        #on créé un nouveau dico avec la fonction Déduction
        dico = Deduction(node1,idRel,node2)
        if(dico != {} and type(dico) != str):
            printResult(dico)
            return True

    #Içi il y a des choix a faire, qu'est ce qu'on fait quand on a pas de résultat ? Est-ce qu'on cherche des relations a poids négatives ? elles indiquent que 
    #la relation cherchée est fausse en attendant je déroule les fonction déjà créée. 

        else:
            #On sait déjà que les deux noeuds sont bien orthographié, ont l'a vérifié dans la fonction direct(), donc on continue notre recherche
            dico = Induction(node1,idRel,node2)
            if(dico != {}):
                printResult(dico)
                return True
            else :
                dico = Synonymes(dico)
                if(dico != {}):
                    return True
                else:    
                    return "On ne sais pas"

#Il y a encore pas mal de trucs a faire comme par exemple exécuter plusieurs stratégies et les ordonnées entres-elles

App("pigeon","r_has_part","atome")