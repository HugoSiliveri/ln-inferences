import sys
import json
import time
import csv
import re
import pickle
import pandas as pd
from pathlib import Path
from sklearn.model_selection import KFold

sys.path.append(str(Path(__file__).resolve().parent.parent))
import api
import utils
import vectorizer

list_rel = ["r_has_causatif","r_has_property-1","r_objet>matiere","r_lieu>origine","r_topic","r_depict","r_holo","r_lieu","r_processus_agent","r_processus_patient","r_processus>instr-1","r_own-1","r_quantificateur","r_social_tie","r_product_of"]
dico_rel = {e:list_rel.index(e) for e in list_rel}

def run_inference(forest=None):
    """
    Lance l'interface de prédiction.
    """
    if forest is None:
        print("loading model")
        try:
            with open("Models/forestModel.pk1", "rb") as f:
                forest = pickle.load(f)
        except FileNotFoundError:
            print("Erreur : Le fichier 'Models/forestModel.pk1' est introuvable.")
            return

    print("Entrez vos triplets (format: 'N de N') ou 'exit' pour sortir.")

    while True:
        saisie = input("\nEntrez un triplé > ").strip()
        if saisie.lower() in ["exit", "quitter"]:
            break
        parts = re.split(r"( de l'| d'une | d'un | des | de | d' | du | de la)", saisie, maxsplit=1, flags=re.IGNORECASE)

        if len(parts) == 3:
            t1, det, t2 = parts[0].strip(), parts[1].strip(), parts[2].strip()
            
            try:
                vec = vectorizer.vectorize_pair(t1, t2, determinant=det)
                
                results = forest.predict([vec])
                res_idx = results[0]
                
                print(f"Résultat : {list_rel[res_idx]}")
                #print(f"Résultat : {str(res_idx)}")
            except Exception as e:
                print(f"Erreur lors de la vectorisation ou prédiction : {e}")
        else:
            print("Format non reconnu. Utilisez 'N de N'")
        
    #Bon et la il faudrait demander à l'utilisateur de rentrer des triplés puis on vectorize, puis on les donnent à la fonction prédict du modèle et on affiche le résultat

if __name__ == "__main__":
    run_inference()
    