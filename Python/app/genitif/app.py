import os
import glob
import pandas as pd
import json
import sys
import time
import math
import predict
from pathlib import Path
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split

CURRENT_DIR = Path(__file__).resolve().parent
CLEANING_PATH = CURRENT_DIR / "dataset" / "aWholeBunchOfDatasets" / "prog_for_dataset"
sys.path.append(str(CLEANING_PATH))

try:
    from cleaning_ds import add_relation_tag
    from vectorizer import vectorize_all_datasets
    from Models.Tree import Forest_Model
except ImportError as e:
    print(f"Erreur d'importation : {e}")
    sys.exit(1)

DATASETS_DIRECTORY = str((CURRENT_DIR / "dataset" / "aWholeBunchOfDatasets" / "Datasets_forever").resolve())
VECTORS = str((CURRENT_DIR / "dataset" / "vectors.json").resolve())

LIST_REL = [
    "r_has_causatif", 
    "r_has_property-1", 
    "r_objet>matière", 
    "r_lieu>origine", 
    "r_topic", 
    "r_depict", 
    "r_holo", 
    "r_lieu", 
    "r_processus_agent", 
    "r_processus_patient", 
    "r_processus>instr-1", 
    "r_own-1", 
    "r_quantificateur", 
    "r_social_tie", 
    "r_product_of"
]
DICO_REL = {e: LIST_REL.index(e) for e in LIST_REL}

def ask(message):
    reponse = input(f"{message} (o/n) : ").lower().strip()
    return reponse == 'o'

def run_pipeline():
    print(f"--- Démarrage du Pipeline ---")
    
    do_cleaning = ask("[1] Lancer le nettoyage des datasets ?")
    do_vectorization = ask("[2] Lancer la vectorisation ?")
    do_training = ask("[3] Lancer l'entrainement du modèle ?")
    do_kfold = ask("[4] Lancer le K-Fold lors de l'entrainement ?")
    do_predict = ask("[5] Lancer la prédiction ?")

    if do_cleaning:
        print("\n>> Action : Nettoyage en cours...")
        search_path = os.path.join(DATASETS_DIRECTORY, "*.csv")
        fichiers_csv = [os.path.basename(f) for f in glob.glob(search_path)]
        
        if fichiers_csv:
            add_relation_tag(DATASETS_DIRECTORY, fichiers_csv)
            print(f"OK : Nettoyage terminé pour {len(fichiers_csv)} fichiers.\n")
        else:
            print(f"Erreur : Aucun fichier CSV trouvé dans {DATASETS_DIRECTORY}\n")

    dataset = None
    if do_vectorization:
        print("\n>> Action : Vectorisation...")
        dataset = vectorize_all_datasets(input_dir=DATASETS_DIRECTORY, output_file=VECTORS)
    
    if dataset is None:
        if os.path.exists(VECTORS):
            with open(VECTORS, "r", encoding="utf-8") as f:
                dataset = json.load(f)
        else:
            if do_training:
                print("Erreur : Fichier absent. Impossible d'entraîner.")
                return

    if do_training and dataset:
        print("\n>> Action : Entrainement du modèle...")
        df = pd.DataFrame.from_records(dataset)
        df["type_relation"] = df["type_relation"].map(DICO_REL)
        
        initial_len = len(df)
        df = df.dropna(subset=["type_relation"])
        df["type_relation"] = df["type_relation"].astype(int)
        
        if len(df) < initial_len:
            print(f"Note : {initial_len - len(df)} lignes ignorées (labels inconnus).")

        forest = Forest_Model(len(LIST_REL))
        #kf = KFold(n_splits=5, shuffle=True, random_state=42)
        dataX = df["features"].to_list()
        acc_scores = []
        count = df["type_relation"].value_counts()
        print("nombre de données dans chaque classe : ")
        print(count)
        count = [count[i] for i in range(15)]
        avg_count = sum(count)/len(count)
        ecart_type_count = math.sqrt(sum([(e-avg_count)**2 for e in count]) / len(count))
        print("l'écart-type est de : "+str(ecart_type_count))
        #min_size_class = min(count)
        #df = pd.concat([df[df["type_relation"] == i].sample(min_size_class) for i in range(len(count))])
        #print(df["type_relation"].value_counts())
        if do_kfold:
            print(f"Lancement du K-Fold sur {len(df)} échantillons...")
            for fold in range(3):
                train_df, test_df = train_test_split(df,random_state=42,test_size=0.05)
                forest.fit(train_df)
                print("Lancement de l'évaluation sur "+str(int(len(df)*0.05))+" data")
                #results = forest.predict(test_df["features"])
                #sum_list = [0]*len(results[0])
                #for L in results:
                #    for c in range(len(L)):
                #        sum_list[c] += L[c]
                #print([sum/len(results) for sum in sum_list])
                start = time.time()
                score = forest.evaluate(test_df)
                end = time.time()
                print("fin de l'évaluation en temps : "+str(end - start))
                acc_scores.append(score)
                print(f"   Fold {fold}/3 | Accuracy : {score:.4f}")
            print("-" * 30)
            print(f"Accuracy Moyenne : {sum(acc_scores)/len(acc_scores):.4f}")
            print("-" * 30)
        print("Entraînement final et sauvegarde du modèle...")
        forest.fit(df)
        forest.save()

    if do_predict:
        try:
            print("\n>> Action : Lancement de l'interface de prédiction...")
            predict.run_inference() 
            
        except ImportError:
            print("Erreur : Le fichier 'predict.py' est introuvable.")
        except Exception as e:
            print(f"Erreur lors de l'exécution de predict.py : {e}")
    
    print("Pipeline terminé avec succès.")

if __name__ == "__main__":
    run_pipeline()