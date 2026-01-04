import requests
import json
import redis
import unicodedata

############### REDIS ###############

r = redis.Redis(host="redis_container", port=6379, db=0)

def store_in_redis(key, value, expiration=604800):
    r.setex(key, expiration, json.dumps(value))

def get_from_redis(key):
    try:
        result = r.get(key)
        return json.loads(result) if result else None
    except Exception:
        return None

#########################################

############### ROUTES API ###############

requests.packages.urllib3.disable_warnings()
BASE_URL = "https://jdm-api.demo.lirmm.fr"
TIMEOUT_VALUE = 10

def get_node_by_id(node_id):
    cache_key = f"node_by_id:{node_id}"
    result = get_from_redis(cache_key)
    if result:
        return result
    
    try:
        response = requests.get(f"{BASE_URL}/v0/node_by_id/{node_id}", verify=False, timeout=TIMEOUT_VALUE)
        response.raise_for_status()
        full_data = response.json()
        
        # On ne stocke que les infos de base du nœud
        filtered_node = {
            "id": full_data.get("id"),
            "name": full_data.get("name"),
            "type": full_data.get("type")
        }
        store_in_redis(cache_key, filtered_node)
        return filtered_node
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        return None

def get_node_by_name(node_name):
    node_name = unicodedata.normalize('NFC', str(node_name).strip())
    cache_key = f"node_by_name:{node_name}"
    
    result = get_from_redis(cache_key)
    if result:
        return result
    
    try:
        response = requests.get(f"{BASE_URL}/v0/node_by_name/{node_name}", verify=False, timeout=TIMEOUT_VALUE)
        response.raise_for_status()
        full_data = response.json()
        
        filtered_node = {
            "id": full_data.get("id"),
            "name": full_data.get("name"),
            "type": full_data.get("type")
        }
        store_in_redis(cache_key, filtered_node)
        return filtered_node
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        return None

def get_relations_from(node_name, parameters):
    node_name = unicodedata.normalize('NFC', str(node_name).strip())
    
    # Correction selon schéma : rel devient types_ids
    if "rel" in parameters:
        parameters["types_ids"] = parameters.pop("rel")
    
    cache_key = f"relations_from:{node_name}_{json.dumps(parameters)}"
    result = get_from_redis(cache_key)
    if result:
        return result
    
    try:
        response = requests.get(f"{BASE_URL}/v0/relations/from/{node_name}", params=parameters, verify=False, timeout=TIMEOUT_VALUE)
        response.raise_for_status()
        full_data = response.json()
        
        # On ne stocke que la liste des relations pour alléger le cache
        filtered_result = {"relations": full_data.get("relations", [])}
        store_in_redis(cache_key, filtered_result)
        return filtered_result
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        return None

def get_relations_from_to(node1_name, node2_name, parameters):
    node1_name = unicodedata.normalize('NFC', str(node1_name).strip())
    node2_name = unicodedata.normalize('NFC', str(node2_name).strip())
    
    if "rel" in parameters:
        parameters["types_ids"] = parameters.pop("rel")
        
    cache_key = f"relations_from_to:{node1_name}_{node2_name}_{json.dumps(parameters)}"
    result = get_from_redis(cache_key)
    if result:
        return result
    
    try:
        response = requests.get(f"{BASE_URL}/v0/relations/from/{node1_name}/to/{node2_name}", params=parameters, verify=False, timeout=TIMEOUT_VALUE)
        response.raise_for_status()
        full_data = response.json()
        
        filtered_result = {"relations": full_data.get("relations", [])}
        store_in_redis(cache_key, filtered_result)
        return filtered_result
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        return None

def get_relations_to(node_name, parameters):
    node_name = unicodedata.normalize('NFC', str(node_name).strip())
    
    if "rel" in parameters:
        parameters["types_ids"] = parameters.pop("rel")
        
    cache_key = f"relations_to:{node_name}_{json.dumps(parameters)}"
    result = get_from_redis(cache_key)
    if result:
        return result
    
    try:
        response = requests.get(f"{BASE_URL}/v0/relations/to/{node_name}", params=parameters, verify=False, timeout=TIMEOUT_VALUE)
        response.raise_for_status()
        full_data = response.json()
        
        filtered_result = {"relations": full_data.get("relations", [])}
        store_in_redis(cache_key, filtered_result)
        return filtered_result
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        return None