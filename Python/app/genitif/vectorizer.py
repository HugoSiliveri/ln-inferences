import sys
import os
import glob
import json
import time
import csv
import pandas as pd
import unicodedata
import copy
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import api
import utils

REL_TYPES = [0, 6, 17]       # Types de relations à extraire (0: r_associated, 3: r_domain, 5: r_syn, 6: r_isa, 17: r_carac)
MAX_REL = 10                   # Limite de relations par type
OUTPUT_FILE = "./dataset/preProcessed_Vectorized.json"

def get_vector_for_term(term: str, side: str):
    term = str(term).strip()
    term = unicodedata.normalize('NFC', term)
    cache_key = f"vectorized_term:{term}"

    try:
        cached_result = api.get_from_redis(cache_key)
        if cached_result:
            # Utilisation de deepcopy pour éviter de muter les données partagées
            return copy.deepcopy(cached_result)
    except Exception as e:
        print(f"Cache inaccessible (lecture) pour '{term}': {e}")

    all_relations = []
    for rtype in REL_TYPES:
        params = {"rel": rtype, "limit": MAX_REL} 
        try:
            data = api.get_relations_from(term, params)

            if not isinstance(data, dict) or "relations" not in data:
                continue
            
            relations_list = data.get("relations", [])
            
            for rel in relations_list:
                try:
                    target_name = utils.get_node_name_by_id(rel["node2"])
                    target_name = clean_term(target_name)
                except (KeyError, AttributeError):
                    target_name = ""

                if target_name:
                    all_relations.append({
                        "side": side,
                        "r_type": rtype,
                        "target": target_name,
                        "weight": float(rel.get("w", 0))
                    })

        except Exception as e:
            print(f"\nErreur API JDM pour le terme '{term}' type {rtype}: {e}")
            raise RuntimeError(f"Term '{term}' skipped") from e
        
        time.sleep(0.2) 

    if all_relations:
        try:
            api.store_in_redis(cache_key, all_relations)
        except Exception as e:
            print(f"Cache inaccessible (écriture) pour '{term}': {e}")

    return copy.deepcopy(all_relations)

def normalize_features(features_list):
    """
    Normalise les poids d'une liste de caractéristiques entre 0 et 1.
    """
    if not features_list:
        return []
        
    weights = [f["weight"] for f in features_list if f["weight"] > 0]
    
    if weights:
        min_w = min(weights)
        max_w = max(weights)
        range_w = max_w - min_w
        
        for f in features_list:
            if f["weight"] > 0:
                if range_w > 0:
                    f["weight"] = f["weight"] / max_w
                else:
                    f["weight"] = 1.0
    return features_list

def vectorize_all_datasets(input_dir="../Datasets_forever/", output_file=OUTPUT_FILE):
    """
    Vectorise tous les fichiers CSV du dossier et affiche les statistiques globales.
    """
    all_files = glob.glob(os.path.join(input_dir, "*.csv"))
    results = []
    global_idx = 0
    total_rows = sum([len(pd.read_csv(f)) for f in all_files])
    
    stats = {
        "total_rows": 0,
        "processed": 0,
        "skipped_no_rel": 0,
        "skipped_incomplete": 0,
        "skipped_error": 0
    }

    for file_path in all_files:
        try:
            df = pd.read_csv(file_path)
            stats["total_rows"] += len(df)
        except Exception:
            continue

        for i, row in df.iterrows():
            global_idx += 1
            A = clean_term(str(row["A"]))
            B = clean_term(str(row["B"]))
            R = str(row.get("determinant", "de")).strip()
            rel_type = row.get("type_relation", "unknown")

            status = f"[{global_idx}/{total_rows}] {A}, {R}, {B}"
            sys.stdout.write(f"\r{status:<100}")
            sys.stdout.flush()

            try:
                raw_vec_A = get_vector_for_term(A, "A")
                raw_vec_B = get_vector_for_term(B, "B")
                
                if not raw_vec_A or not raw_vec_B:
                    stats["skipped_no_rel"] += 1
                    continue

                norm_A = normalize_features(raw_vec_A)
                norm_B = normalize_features(raw_vec_B)
                combined = norm_A + norm_B
                combined.append({"side": "R", "r_type": "prep", "target": R, "weight": 1.0})
                
                tree_structure = convert_to_tree_structure(combined)

                if all(k in tree_structure for k in ["A", "B", "R"]):
                    results.append({
                        "A": A, "R": R, "B": B,
                        "type_relation": rel_type,
                        "features": tree_structure
                    })
                    stats["processed"] += 1
                else:
                    stats["skipped_incomplete"] += 1
            except Exception:
                stats["skipped_error"] += 1
                continue

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("\n")
    print("-" * 35)
    print(f"Lignes totales lues     : {stats['total_rows']}")
    print(f"Lignes sauvegardées     : {stats['processed']}")
    print(f"Lignes sans relations   : {stats['skipped_no_rel']}")
    print(f"Lignes incomplètes      : {stats['skipped_incomplete']}")
    print(f"Lignes erreurs API      : {stats['skipped_error']}")
    print("-" * 35)
    
    return results

def convert_to_tree_structure(flat_features_list):
    """
    Convertit la liste plate de dictionnaires en une structure arborescente (dict imbriqué).
    """
    tree = {"A": {}, "B": {}, "R": {}}
    for f in flat_features_list:
        side = f['side']
        r_type = str(f['r_type'])
        target = f['target']
        weight = f['weight']
        
        if r_type not in tree[side]:
            tree[side][r_type] = {}
        tree[side][r_type][target] = weight
    return tree

def clean_term(term):
    """
    Supprime les articles pour obtenir le mot seul.
    Exemple: "le mannequin" -> "mannequin", "l'ouvrier" -> "ouvrier"
    """
    articles = ["le ", "la ", "les ", "l'", "un ", "une ", "des ", "du ", "au ", "d'"]
    t = term.lower().strip()
    for art in articles:
        if t.startswith(art):
            return term[len(art):].strip()
    return term

def vectorize_pair(t1, t2, determinant):
    """
    Transforme un couple de mots au format identique à celle du dataset d'entraînement.
    """
    A = clean_term(t1)
    B = clean_term(t2)
    R = determinant.strip()

    # Récupération des vecteurs bruts
    raw_vec_A = get_vector_for_term(A, "A")
    raw_vec_B = get_vector_for_term(B, "B")

    # Normalisation
    norm_A = normalize_features(raw_vec_A)
    norm_B = normalize_features(raw_vec_B)

    # Combinaison et formatage en arbre
    combined = norm_A + norm_B
    combined.append({"side": "R", "r_type": "prep", "target": R, "weight": 1.0})
    
    return convert_to_tree_structure(combined)


#print("Création d'un petit dataset aléatoire pour test")
#sample_file = create_sample_dataset(sample_size=50)

#print("Démarrage de la vectorisation via API JeuxDeMots")
#vectorize_dataset(input_file=sample_file)