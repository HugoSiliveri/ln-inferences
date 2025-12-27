import sys
import json
import time
import csv
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import api
import utils

REL_TYPES = [0, 3, 5, 6, 17]       # Types de relations à extraire (0: r_associated, 3: r_domain, 5: r_syn, 6: r_isa, 17: r_carac)
MAX_REL = 10                   # Limite de relations par type
INPUT_FILE = "adeb/dataset/preProcessed_Dataset.csv"
OUTPUT_FILE = "adeb/dataset/preProcessed_Vectorized.csv"


def get_vector_for_term(term: str, side: str):
    """
    Récupère les relations JDM pour un terme donné (A ou B).
    Gère les erreurs Redis de manière non-bloquante pour éviter l'arrêt du script.
    """
    term = str(term).strip().lower()
    cache_key = f"vectorized_term:{term}"

    try:
        cached_result = api.get_from_redis(cache_key)
        if cached_result:
            return cached_result
    except Exception as e:
        print(f"Cache inaccessible (lecture) pour '{term}': {e}")

    all_relations = []
    for rtype in REL_TYPES:
        params = {"rel": rtype}
        try:
            data = api.get_relations_from(term, params)

            if not data or "relations" not in data:
                continue

            for rel in data["relations"][:MAX_REL]:
                try:
                    target_name = utils.get_node_name_by_id(rel["node2"])
                except (KeyError, AttributeError):
                    target_name = ""

                all_relations.append({
                    "side": side,
                    "r_type": rtype,
                    "target": target_name,
                    "weight": rel.get("w", 0)
                })

        except Exception as e:
            print(f"Erreur API JDM pour le terme '{term}' type {rtype}: {e}")
            raise RuntimeError(f"Term '{term}' skipped à cause d'une erreur API") from e

        time.sleep(0.15)  # Respect du quota API
    if all_relations:
        try:
            api.store_in_redis(cache_key, all_relations)
        except Exception as e:
            print(f"Cache inaccessible (écriture) pour '{term}': {e}")

    return all_relations


def create_sample_dataset(input_file=INPUT_FILE, output_file="adeb/dataset/sample_Dataset.json", sample_size=50):
    """
    Crée un petit dataset aléatoire à partir du dataset complet.
    """
    if not Path(output_file).exists():
        df = pd.read_csv(input_file)
        
        if sample_size > len(df):
            sample_size = len(df)
        
        sample_df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
        sample_df.to_csv(output_file, index=False, encoding="utf-8", quoting=csv.QUOTE_ALL)
        
        print(f"Sample de {sample_size} lignes créé : {output_file}")
    else:
        print(f"Le sample existe déjà")
    
    return output_file


def vectorize_dataset(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """
    Lit le dataset, crée un CSV vectorisé basé sur les relations JDM,
    normalise les poids (Min-Max) JDM ligne par ligne, et ajoute la relation R (poids 1.0).
    """
    df = pd.read_csv(input_file)
    results = []

    total_rows = len(df)
    processed = 0
    skipped = 0

    for i, row in df.iterrows():
        A = str(row["A"]).strip()
        R = str(row["R"]).strip().lower()
        B = str(row["B"]).strip()
        rel_type = row["type_relation"]

        print(f"[{i+1}/{total_rows}] Traitement : {A} {R} {B}")

        try:
            vec_A = get_vector_for_term(A, "A")
            vec_B = get_vector_for_term(B, "B")
        except RuntimeError:
            skipped += 1
            print(f"Skipping la ligne {i+1} ({A}, {B}) à cause d'une erreur API")
            continue

        processed += 1
        
        combined_jdm = vec_A + vec_B
        
        jdm_weights = [f["weight"] for f in combined_jdm if f["weight"] > 0]
        
        if jdm_weights:
            min_w = min(jdm_weights)
            max_w = max(jdm_weights)
            
            if max_w > min_w:
                range_w = max_w - min_w
                for f in combined_jdm:
                    if f["weight"] > 0:
                        # Formule de Normalisation: (X - Min) / (Max - Min)
                        f["weight"] = (f["weight"] - min_w) / range_w
            # Cas où tous les poids sont identiques mais > 0
            elif max_w > 0:
                for f in combined_jdm:
                    if f["weight"] > 0:
                        f["weight"] = 1.0 # Tous les poids égaux deviennent 1.0

        combined_features = combined_jdm
        combined_features.append({"side": "R", "r_type": "prep", "target": R, "weight": 1.0})

        tree_structure = convert_to_tree_structure(combined_features)

        #features_json_string = json.dumps(tree_structure, ensure_ascii=False)
        
        results.append({
            "A": A,
            "R": R,
            "B": B,
            "type_relation": rel_type,
            "features": tree_structure
        })
    with open(output_file,"w") as f:
        json.dump(results,f)
    #pd.DataFrame(results).to_csv(output_file, index=False, encoding="utf-8")

    print(f"Vectorisation terminée : {output_file}")
    print(f"Lignes totales : {total_rows}")
    print(f"Lignes traitées : {processed}")
    print(f"Lignes ignorées : {skipped}")
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
    print("Création d'un petit dataset aléatoire pour test")
    sample_file = create_sample_dataset(sample_size=50)

    print("Démarrage de la vectorisation via API JeuxDeMots")
    vectorize_dataset(input_file=sample_file)