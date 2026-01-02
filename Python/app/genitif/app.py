import os
import glob
import pandas as pd
import json
import sys
from pathlib import Path
from sklearn.model_selection import KFold

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
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        dataX = df["features"].to_list()
        acc_scores = []
        
        print(f"Lancement du K-Fold sur {len(df)} échantillons...")
        for fold, (train_ix, test_ix) in enumerate(kf.split(dataX), 1):
            train_df = df.iloc[train_ix]
            test_df = df.iloc[test_ix]
            forest.fit(train_df)
            score = forest.evaluate(test_df)
            acc_scores.append(score)
            print(f"   Fold {fold}/5 | Accuracy : {score:.4f}")
        
        print("-" * 30)
        print(f"Accuracy Moyenne : {sum(acc_scores)/len(acc_scores):.4f}")
        print("-" * 30)

        print("Entraînement final et sauvegarde du modèle...")
        forest.fit(df)
        forest.save()
        print("Pipeline terminé avec succès.")

if __name__ == "__main__":
    run_pipeline()