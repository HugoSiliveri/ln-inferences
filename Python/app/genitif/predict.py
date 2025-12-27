import sys
import json
import time
import csv
import pandas as pd
from pathlib import Path
from sklearn.model_selection import KFold

sys.path.append(str(Path(__file__).resolve().parent.parent))
import api
import utils
import vectorizer

list_rel = ["r_has_causatif","r_has_property-1","r_objet>matiere","r_lieu>origine","r_topic","r_depict","r_holo","r_lieu","r_processus_agent","r_processus_patient","r_processus>instr-1","r_own-1","r_quantificateur","r_social_tie","r_product_of"]
dico_rel = {e:list_rel.index(e) for e in list_rel}

#TODO ajouter la partie du programme qui demande un triplé à l'utilisateur, le parse, puis l'envoie à la fonction prédicte et affiche le résultat
if __name__ == "__main__":
    print("loading model")
    with open("models/forestModel.pk1","rb") as f:
        forest = pickle.load(f)
    #Bon et la il faudrait demander à l'utilisateur de rentrer des triplés puis on vectorize, puis on les donnent à la fonction prédict du modèle et on affiche le résultat