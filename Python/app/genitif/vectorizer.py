import sys
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

REL_TYPES = [0, 3, 5, 6, 17]       # Types de relations à extraire (0: r_associated, 3: r_domain, 5: r_syn, 6: r_isa, 17: r_carac)
MAX_REL = 10                   # Limite de relations par type
INPUT_FILE = "./dataset/preProcessed_Dataset.csv"
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
                    f["weight"] = (f["weight"] - min_w) / range_w
                else:
                    f["weight"] = 1.0
    return features_list

def vectorize_dataset(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """
    Lit le dataset, crée un JSON vectorisé et filtre strictement les triplets.
    Affiche la progression via sys.stdout.write.
    """
    df = pd.read_csv(input_file)
    results = []

    total_rows = len(df)
    processed = 0
    skipped_no_rel = 0
    skipped_error = 0
    skipped_incomplete = 0

    required_types = [str(rtype) for rtype in REL_TYPES]

    for i, row in df.iterrows():
        A = str(row["A"]).strip()
        R = str(row["R"]).strip()
        B = str(row["B"]).strip()
        rel_type = row["type_relation"]

        status_line = f"[{i+1}/{total_rows}] {A}, {R}, {B}"
        sys.stdout.write(f"\r{status_line:<100}") 
        sys.stdout.flush()

        try:
            raw_vec_A = get_vector_for_term(A, "A")
            raw_vec_B = get_vector_for_term(B, "B")
            
            if not raw_vec_A or not raw_vec_B:
                skipped_no_rel += 1
                continue
            norm_A = normalize_features(raw_vec_A)
            norm_B = normalize_features(raw_vec_B)

            combined = norm_A + norm_B
            combined.append({"side": "R", "r_type": "prep", "target": R, "weight": 1.0})

            tree_structure = convert_to_tree_structure(combined)

            has_A = all(t in tree_structure.get("A", {}) for t in required_types)
            has_B = all(t in tree_structure.get("B", {}) for t in required_types)
            has_R = "R" in tree_structure

            if has_A and has_B and has_R:
                processed += 1
                results.append({
                    "A": A,
                    "R": R,
                    "B": B,
                    "type_relation": rel_type,
                    "features": tree_structure
                })
            else:
                skipped_incomplete += 1

        except RuntimeError:
            skipped_error += 1
            continue

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("\n")
    print("-" * 30)
    print(f"Lignes totales lues   : {total_rows}")
    print(f"Lignes sauvegardées   : {processed}")
    print(f"Lignes sans relations : {skipped_no_rel}")
    print(f"Lignes incomplètes    : {skipped_incomplete}")
    print(f"Lignes erreurs API    : {skipped_error}")
    print("-" * 30)
    
    return results

def convert_to_tree_structure(flat_features_list):
    """
    Convertit la liste plate de dictionnaires en une structure arborescente (dict imbriqué).
    """
    tree = {}
    for f in flat_features_list:
        side = f['side']
        r_type = str(f['r_type'])
        target = f['target']
        weight = f['weight']
        
        if side not in tree:
            tree[side] = {}
        if r_type not in tree[side]:
            tree[side][r_type] = {}
            
        tree[side][r_type][target] = weight
    return tree

if __name__ == "__main__":
    #print("Création d'un petit dataset aléatoire pour test")
    #sample_file = create_sample_dataset(sample_size=50)

    #print("Démarrage de la vectorisation via API JeuxDeMots")
    #vectorize_dataset(input_file=sample_file)
    vectorize_dataset()