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
        self.distance_to_max_weight = 0.05
        if(List_Vector is None):
            self.root=None
        if(isinstance(List_Vector,TreeNode)):
            self.root=List_Vector
        if(type(List_Vector) is list):
            self.Build_Tree(List_Vector)

    # Version de Gemini qui fixe le prob de KeyError
    def compute_scores(self, v1, v2):
        done = {"A": {}, "B": {}, "R": {}}
        v3 = {"A": {}, "B": {}, "R": {}}
        sim = []
        max_weight = {"A": {},"B": {},"R": {}}
        for k0 in ["A", "B", "R"]:
            for k1 in v1[k0].keys():
                v3[k0][k1] = {}
                max_weight[k0][k1] = 0
                # VERIFICATION : si la relation (ex: '3') n'est pas dans v2, on ne peut pas faire de dictionnaire done
                if k1 in v2[k0]:
                    if k1 not in done[k0]:
                        done[k0][k1] = {key: False for key in v2[k0][k1].keys()}
                    
                    for word in v1[k0][k1].keys():
                        leafs = v2[k0][k1].keys()
                        if word in leafs:
                            weight = (v1[k0][k1][word] + v2[k0][k1][word]) / 2
                            v3[k0][k1][word] = weight
                            if weight > max_weight[k0][k1]:
                                max_weight[k0][k1] = weight
                            sim.append(abs(v1[k0][k1][word] - v2[k0][k1][word]))
                            done[k0][k1][word] = True
                        else:
                            weight = v1[k0][k1][word] / 2
                            if weight > max_weight[k0][k1]:
                                max_weight[k0][k1] = weight
                            v3[k0][k1][word] = weight
                            sim.append(abs(v1[k0][k1][word]))
                else:
                    # Cas où k1 est dans v1 mais pas dans v2
                    for word in v1[k0][k1].keys():
                        weight = v1[k0][k1][word] / 2
                        v3[k0][k1][word] = weight
                        if weight > max_weight[k0][k1]:
                                max_weight[k0][k1] = weight
                        sim.append(abs(v1[k0][k1][word]))

        # Second passage pour v2
        for k0 in ["A", "B", "R"]:
            for k1 in v2[k0].keys():
                if k1 not in v3[k0]:
                    v3[k0][k1] = {}
                    max_weight[k0][k1] = 0
                for word in v2[k0][k1]:
                    # Utilisation de .get() sécurisé pour éviter KeyError
                    if k1 not in done[k0] or not done[k0][k1].get(word, False):
                        weight = v2[k0][k1][word] / 2
                        if weight > max_weight[k0][k1]:
                                max_weight[k0][k1] = weight
                        v3[k0][k1][word] = weight
                        sim.append(abs(v2[k0][k1][word]))
        
        #On enlève tout ce qui est trop loin du plus grand poid
        final_vector = {"A": {}, "B": {}, "R": {}}
        for k0 in ["A","B","R"]:
            for k1 in v3[k0].keys():
                final_vector[k0][k1] = {}
                for word in v3[k0][k1]:
                    if v3[k0][k1][word] > self.distance_to_max_weight * max_weight[k0][k1]:
                        final_vector[k0][k1][word] = v3[k0][k1][word]
        return final_vector, sum(sim) / len(sim) if sim else 0
    """
    Version de Lucien
    def compute_scores(self,v1,v2):
        #Pour chaque donnée du vecteur v1 on cherche si elle existe dans v2
        done = {"A":{},"B":{},"R":{}}
        v3 = {"A":{},"B":{},"R":{}}
        sim = []
        for k0 in ["A","B","R"]:
            for k1 in v1[k0].keys():
                v3[k0][k1]={}
                if not(k1 in done[k0].keys()):
                    try :
                        done[k0][k1] = {key:False for key in v2[k0][k1].keys()}#Hopefully ça marche
                    except KeyError :
                        print(done)
                        print(v2)
                        print("liste des index a suivre dans leur ordre")
                        print("0 : "+str(k0)+" , 1 : "+str(k1))
                for word in v1[k0][k1].keys():
                    leafs = v2[k0][k1].keys()
                    if word in leafs:
                        v3[k0][k1][word] = (v1[k0][k1][word] + v2[k0][k1][word])/2
                        sim.append(abs(v1[k0][k1][word] - v2[k0][k1][word]))
                        done[k0][k1][word]=True
                    else:
                        v3[k0][k1][word] = v1[k0][k1][word]/2
                        sim.append(abs(v1[k0][k1][word]))
        for k0 in ["A","B","R"]:
            for k1 in v2[k0].keys():
                for word in v2[k0][k1]:
                    if not(done[k0][k1][word]):
                        v3[k0][k1][word] = v2[k0][k1][word]/2
                        sim.append(abs(v2[k0][k1][word]))
        return v3 , sum(sim) / len(sim)
    """
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
            #print(list_sim)
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
