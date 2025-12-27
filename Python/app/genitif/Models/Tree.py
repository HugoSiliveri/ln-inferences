import pickle

class TreeNode:
    def __init__(self, data, left = None, right = None):
        self.data = data
        self.left = left
        self.right = right
    def print(self, prefix="", is_left=True):#Made by GPT
        if self is None:
            return
        if self.right != None:
            self.right.print(prefix + ("│   " if is_left else "    "), False)
        print(prefix + ("└── " if is_left else "┌── ") + str(self.data))
        if self.left != None:
            self.left.print(prefix + ("    " if is_left else "│   "), True)

class Tree:
    def __init__(self,List_Vector=None):
        if(List_Vector is None):
            self.root=None
        if(isinstance(List_Vector,TreeNode)):
            self.root=List_Vector
        if(type(List_Vector) is list):
            self.Build_Tree(List_Vector)
    def compute_scores(self,v1,v2):
        #Pour chaque donnée du vecteur v1 on cherche si elle existe dans v2
        done = {"A":{},"B":{}}
        v3 = {"A":{},"B":{}}
        sim = []
        for k0 in ["A","B"]:
            for k1 in v1[k0].keys():
                v3[k0][k1]={}
                if not(k1 in done[k0].keys()):
                    done[k0][k1] = {key:False for key in v2[k0][k1].keys()}#Hopefully ça marche
                for word in v1[k0][k1].keys():
                    leafs = v2[k0][k1].keys()
                    if word in leafs:
                        v3[k0][k1][word] = (v1[k0][k1][word] + v2[k0][k1][word])/2
                        sim.append(abs(v1[k0][k1][word] - v2[k0][k1][word]))
                        done[k0][k1][word]=True
                    else:
                        v3[k0][k1][word] = v1[k0][k1][word]/2
                        sim.append(abs(v1[k0][k1][word]))
        for k0 in ["A","B"]:
            for k1 in v2[k0].keys():
                for word in v2[k0][k1]:
                    if not(done[k0][k1][word]):
                        v3[k0][k1][word] = v2[k0][k1][word]/2
                        sim.append(abs(v2[k0][k1][word]))
        return v3 , sum(sim) / len(sim)
    def Build_Tree(self,List_Vector):
        def find_closest_to_first(List_Vector):#Cherche systématiquement le vecteur le proche de celui en position 0
            #Trouve les vecteurs les plus proche
            first_node_data = List_Vector[0].data
            v_score, min_sim = self.compute_scores(first_node_data,List_Vector[1].data)
            sim_index = 1
            for j in range(2,len(List_Vector)):
                v1,v2 = first_node_data,List_Vector[j].data
                #print("comparing : "+str(v1)+" and "+str(v2))
                v_score, sim = self.compute_scores(v1,v2)
                #print(sim)
                if sim < min_sim :
                    min_sim = sim
                    sim_index = j
            return sim_index, v_score
        def Build_tree_level(current_level):
            next_tree_level = []
            while len(current_level) > 1 :#Actuellement on cherche la plus grande similarité entre deux neouds etc jusq'à ce qu'il n'y ait plus deux noeuds a comparer, cette méthode ne permet pas forcément d'obtenir la meilleur similarité moyenne
                id2, score = find_closest_to_first(current_level)
                node = TreeNode(score,current_level[0],current_level[id2])
                next_tree_level.append(node)
                current_level.pop(id2)#id1 est toujours plus petit que id2, on supprime donc id2 d'abord
                current_level.pop(0)
            if len(current_level) == 1:
                next_tree_level.append(current_level.pop(0))#Quel est le score d'un noeud qui as un seul enfant (dans le cas d'un vecteur on pourais dire que c'est l'unique vecteur de son fils)
            return next_tree_level
        
        #List_Vector est une liste de couple pour lesquels chaque couple correspond a un vecteur avec (n1,n2) n1 et n2 des scores calculés a partir des relations sem.
        current_level = [TreeNode(e) for e in List_Vector]
        while len(current_level) > 1:
            current_level = Build_tree_level(current_level)
        self.root = current_level[0]
    def inference(self,data):
        if not(self.root is None):
            #La méthode prend une unique donnée en entrée et renvoie le score de similarité
            vector, root_score = self.compute_scores(self.root.data,data)
            if not(self.root.right is None) and not(self.root.left is None):
                child_score = min(Tree(self.root.right).inference(data),Tree(self.root.left).inference(data))
                return min(child_score,root_score)
            if not(self.root.right is None) and (self.root.left is None):
                return min(Tree(self.root.right).inference(data),root_score)
            if (self.root.right is None) and not(self.root.left is None):
                return min(Tree(self.root.left).inference(data),root_score)
            if (self.root.right is None) and (self.root.left is None):
                return root_score
        else :
            return 10000 #Ca c'est vraiment brouillon mais tkt
    def print(self):
        self.root.print()

#TODO tester la putain de classe avec tout les arbres et trouver comment save le bordel
class Forest_Model:
    def __init__(self,nbClasses):
        self.nbClasses = nbClasses
        self.Trees=[]
        for i in range(nbClasses):
            self.Trees.append(Tree())
    def fit(self,dataframe):
        for i in range(self.nbClasses):
            List_Vector = dataframe[dataframe["type_relation"] == i]['features'].to_list()
            if(len(List_Vector) < 1):
                print("il n'y a pas de données pour la classe : "+str(i))
            else :
                self.Trees[i].Build_Tree(List_Vector)
    def predict(self,data):
        result = []
        for d in data:
            list_sim = [e.inference(d) for e in self.Trees]
            print(list_sim)
            min_sim = list_sim[0]
            index = 0
            for i in range(1,len(list_sim)):
                if min_sim > list_sim[i]:
                    min_sim = list_sim[i]
                    index = i
            result.append(index)
        return result
    def evaluate(self,dataframe):
        prediction = self.predict(dataframe["features"])
        tag = dataframe["type_relation"].to_list()
        true = 0
        for i in range(len(prediction)):
            if(prediction[i] == tag[i]):
                true +=1
        return true/len(prediction)
    def save(self):
        with open('models/forestModel.pk1',"wb") as f:
            pickle.dump(self,f,pickle.HIGHEST_PROTOCOL)



#Trouver comment faire les calculs sur le GPI


def parse_tree_vect(L):
    for d in L:
        print(d)
        id = d.find("\"\"")

###### exemple de test #######
#L = [
#    [{"side": "A", "r_type": 0, "target": "rançonnement", "weight": 4.0},{"side": "B", "r_type": 0, "target": "discréditer", "weight": 35.0},],
#    [{"side": "A", "r_type": 0, "target": "rançonnement", "weight": 27.0},{"side": "B", "r_type": 0, "target": "discréditer", "weight": 12.0},],
#    [{"side": "A", "r_type": 0, "target": "rançonnement", "weight": 27.0},{"side": "B", "r_type": 0, "target": "patate", "weight": 12.0},],
#    [{"side": "A", "r_type": 0, "target": "maaaaageeerr", "weight": 27.0},{"side": "B", "r_type": 0, "target": "bibobo", "weight": 12.0},],
#    [{"side": "B", "r_type": 0, "target": "discréditer", "weight": 35.0},{"side": "A", "r_type": 0, "target": "rançonnement", "weight": 4.0},]]

import json
import pandas as pd
list_rel = ["r_has_causatif","r_has_property-1","r_objet>matiere","r_lieu>origine","r_topic","r_depict","r_holo","r_lieu","r_processus_agent","r_processus_patient","r_processus>instr-1","r_own-1","r_quantificateur","r_social_tie","r_product_of"]
dico_rel = {e:list_rel.index(e) for e in list_rel}

df = pd.read_json("dataset/preProcessed_Vectorized.json")
df["type_relation"] = df["type_relation"].map(dico_rel)


with open("models/forestModel.pk1","rb") as f:
    forest = pickle.load(f)
print(forest.evaluate(df.head(15)))

exit()
df = pd.read_json("dataset/preProcessed_Vectorized.json")
df["type_relation"] = df["type_relation"].map(dico_rel)
#print(df.head())
#tree = Tree(list(df["features"].head()))
#tree.root.print()
#print("Combien de classes différentes : "+str(df["type_relation"].value_counts()))
forest = Forest_Model(15)
from sklearn.model_selection import KFold
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






exit()
forest.fit(df.head(45))
#print(df.head(1)["features"].to_list())
print(df.tail(5)["type_relation"].to_list())
print(forest.predict(df.tail(5)["features"].to_list()))


#Ca c'est de la merde
#df = pd.read_csv("Python/app/adeb/dataset/preProcessed_Vectorized.csv")#n'importe pas la colonne features
#print(df.head())
#df["type_relation"] = df["type_relation"].map(dico_rel)
#df = df["features"]
#L = list(df.head(5))

#tree = Tree(L)
#tree.root.print()
#print(tree.inference([{"side": "B", "r_type": 0, "target": "discréditer", "weight": 35.0},{"side": "A", "r_type": 0, "target": "rançonnement", "weight": 14.0},]))


###### New tests encore plus vénères ######

