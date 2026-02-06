import pickle
from Models.Tree import Forest_Model
from train import train_model
from sklearn.model_selection import train_test_split
import pandas as pd
import pickle
import time
import json

#with open('dataset/.json') as f:
#        dataset = json.load(f)

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
#df = pd.DataFrame.from_records(dataset)
#df["type_relation"] = df["type_relation"].map(DICO_REL)
#forest = Forest_Model(len(list_rel))
#forest.fit(df)

#df = pd.read_csv("Python/app/genitif/dataset/aWholeBunchOfDatasets/Datasets_forever/first_version/r_objet_matière_full.csv")
#df = df.sample(1150)
#df.to_csv("Python/app/genitif/dataset/aWholeBunchOfDatasets/Datasets_forever/r_objet_matière.csv")

class MyCustomUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
                if module == "__main__":
                        module = "Models.Tree"
                return super().find_class(module, name)

with open("Python/app/genitif/models/forestModel.pk1", 'rb') as f:
        unpickler = MyCustomUnpickler(f)
        forest = unpickler.load()

root_1_data = forest.Trees[0].root.data

#for key in root_1_data["A"].keys():
#        print(root_1_data["A"][key])


#with open("Python/app/genitif/dataset/vectors.json") as json_file:
#        dataset = json.load(json_file)

dataset = pd.read_json("Python/app/genitif/dataset/vectors.json")

count = dataset["type_relation"].value_counts()
print(count)
print(min(count))
print(len(count))

exit()
sub_dataset = dataset.sample(10)
print(sub_dataset["type_relation"].apply(lambda x: LIST_REL.index(x)))
classif_results = forest.predict(sub_dataset["features"])
for l in classif_results:
        print(l.index(min(l)))

avg = [0]*len(classif_results[0])
for i in range(len(classif_results)):
        for j in range(len(classif_results[i])):
                avg[j]+= classif_results[i][j]

avg = [e/len(classif_results[0]) for e in avg]

print(avg)

###### dont go below #####
exit()
with open("Python/app/genitif/dataset/preProcessed_Vectorized.json") as json_file:
        dataset = json.load(json_file)
print(len(dataset))
exit()
df = pd.DataFrame.from_records(dataset)
df["type_relation"] = df["type_relation"].map(DICO_REL)

train_set, test_set = train_test_split(df,random_state=42,test_size=0.2)
print(type(train_set))
print(df.head())

start = time.time()
print(forest.evaluate(df))
end = time.time()
print("temps d'inférence : "+str(end-start))

#forest.Trees[4].inference(dataset[0]["features"])

#TODO afficher la cardinalité des classes après vectorization, puis changer la taille du jeu de test k-fold parce que vas y quoi ...

#while not (node is None):
#        vector = node.data
#        print("niveau "+str(niveau))
#        for i in ["A","B"]:
#                for j in vector[i].keys():
#                        print("node "+i+" relation type "+str(j)+" nb relations : "+str(len(vector[i][j])))
#        node = node.left
#        niveau+=1




#def count_nodes(root):
#        count_right = 0
#        count_left = 0
#        if not(root.right is None):
#                count_right = count_nodes(root.right)
#        if not(root.left is None):
#                count_left = count_nodes(root.left)
#        return 1 + count_left + count_right
#
#print("nb noeuds dans le premier arbre = " + str(count_nodes(forest.Trees[1].root)))
#
#count_total = 0
#for t in forest.Trees:
#        count_total += count_nodes(t.root)
#print("nombre de noeuds au total dans la foret : "+str(count_total))

