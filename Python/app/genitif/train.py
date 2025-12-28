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
from Models.Tree import Forest_Model

list_rel = ["r_has_causatif","r_has_property-1","r_objet>matiere","r_lieu>origine","r_topic","r_depict","r_holo","r_lieu","r_processus_agent","r_processus_patient","r_processus>instr-1","r_own-1","r_quantificateur","r_social_tie","r_product_of"]
dico_rel = {e:list_rel.index(e) for e in list_rel}

if __name__ == "__main__":
    
    print("Vectorisation du jeu de données")
    dataset = vectorizer.vectorize_dataset(input_file="genitif/dataset/preProcessed_Dataset.csv")
    print("Entrainement du modèle")
    df = pd.DataFrame.from_records(dataset)
    df["type_relation"] = df["type_relation"].map(dico_rel)
    forest = Forest_Model(15)
    #On vas faire un petit kFold avant quand même histoire de faire les choses bien
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    dataX = df["features"].to_list()
    dataY = df["type_relation"].to_list()
    acc = []
    for train_ix, test_ix in kf.split(dataX):
        print(train_ix,test_ix)
        train = df.iloc[train_ix]
        test = df.iloc[test_ix]
        forest.fit(train)
        acc.append(forest.evaluate(test))
    print("accuracy : "+str(sum(acc) / len(acc)))
    forest.fit(df)
    forest.save()




