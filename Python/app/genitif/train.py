import sys
import pandas as pd
from pathlib import Path
from sklearn.model_selection import KFold

sys.path.append(str(Path(__file__).resolve().parent.parent))
from Models.Tree import Forest_Model

def train_model(dataset):
    """
    Fonction appelée par app.py pour entraîner la forêt.
    """
    print("[2] Entraînement du modèle")
    
    df = pd.DataFrame.from_records(dataset)
    
    df["type_relation"] = df["type_relation"].map(dico_rel)
    
    df = df.dropna(subset=["type_relation"])
    df["type_relation"] = df["type_relation"].astype(int)
    
    forest = Forest_Model(len(list_rel))
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    dataX = df["features"].to_list()
    acc = []
    
    for fold, (train_ix, test_ix) in enumerate(kf.split(dataX), 1):
        train_df = df.iloc[train_ix]
        test_df = df.iloc[test_ix]
        forest.fit(train_df)
        score = forest.evaluate(test_df)
        acc.append(score)
        print(f"   Fold {fold}/5 - Accuracy : {score:.4f}")
    
    print(f"Accuracy moyenne : {sum(acc) / len(acc):.4f}")
    
    forest.fit(df)
    forest.save()
    
    return forest




