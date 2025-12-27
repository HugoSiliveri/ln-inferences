import requests
import json
import redis

############### REDIS ###############

r = redis.Redis(host="redis_container", port=6379, db=0)

def store_in_redis(key, value, expiration=604800): # TTL 1 semaine
    r.setex(key, expiration, json.dumps(value))

def get_from_redis(key):
    result = r.get(key)
    return json.loads(result) if result else None

#########################################
 

############### ROUTES API ###############

requests.packages.urllib3.disable_warnings() 
url = "https://jdm-api.demo.lirmm.fr"

def get_node_by_id(node_id):
    cache_key = f"node_by_id:{node_id}"
    result = get_from_redis(cache_key)
    if result:
        return result
    else: 
        response = requests.get(f"{url}/v0/node_by_id/{node_id}", verify=False)
        response.raise_for_status()
        result = response.json()
        store_in_redis(cache_key, response.json())
        return result

def get_node_by_name(node_name):
    cache_key = f"node_by_name:{node_name}"
    result = get_from_redis(cache_key)
    if result:
        return result
    else:
        response = requests.get(f"{url}/v0/node_by_name/{node_name}", verify=False)
        response.raise_for_status()
        result = response.json()
        store_in_redis(cache_key, result)
        return result

def get_relations_from(node_name, parameters):
    cache_key = f"relations_from:{node_name}_{json.dumps(parameters)}"
    result = get_from_redis(cache_key)
    if result:
        return result
    else:
        response = requests.get(f"{url}/v0/relations/from/{node_name}", params=parameters, verify=False)
        response.raise_for_status()
        result = response.json()
        store_in_redis(cache_key, result)
        return result

def get_relations_from_to(node1_name, node2_name, parameters):
    cache_key = f"relations_from_to:{node1_name}_{node2_name}_{json.dumps(parameters)}"
    result = get_from_redis(cache_key)
    if result:
        return result
    else:
        response = requests.get(f"{url}/v0/relations/from/{node1_name}/to/{node2_name}", params=parameters, verify=False)
        response.raise_for_status()
        result = response.json()
        store_in_redis(cache_key, result)
        return result

def get_relations_to(node_name, parameters):
    cache_key = f"relations_to:{node_name}_{json.dumps(parameters)}"
    result = get_from_redis(cache_key)
    if result:
        return result
    else:
        response = requests.get(f"{url}/v0/relations/to/{node_name}", params=parameters, verify=False)
        response.raise_for_status()
        result = response.json()
        store_in_redis(cache_key, result)
        return result


#########################################