import re
import pandas as pd
L = ["des","de la","de","du","d'un","d'une","d'"]

def preprocess_topictxt(file_path):
    with open(file_path,"r") as f:
        content = f.read()
    lines = re.split(r'\n',content)
    A = []
    determinant = []
    B = []
    for i in range(1,len(lines)):
        index = -1
        cpt=0
        while (index == -1) and (cpt < len(L)-1):
            index = lines[i].find(" "+L[cpt]+" ")
            cpt+=1
        if index == -1:#On cherche le d' sans l'accent après l'apostrophe
            index = lines[i].find(" "+L[cpt])
            cpt+=1
            if index ==-1:
                print("WTF ????")
                print(lines[i])
            else :
                a = lines[i][:index]
                det = lines[i][index+1:index+1+len(L[cpt-1])]
                b = lines[i][index+1+len(L[cpt-1]):]
                A.append(a);determinant.append(det);B.append(b)
        else :
            a = lines[i][:index]
            det = lines[i][index+1:index+1+len(L[cpt-1])]
            b = lines[i][index+2+len(L[cpt-1]):]
            A.append(a);determinant.append(det);B.append(b)
    df = pd.DataFrame({"A": A,"determinant": determinant,"B": B})
    print(df.head())
    df.to_csv("../Datasets_forever/r_topic.csv",index=False)

def preprocess_r_objet_matière(file_path):
    df = pd.read_csv(file_path)
    print(df.head())
    df = df[["A","determinant","B"]]
    print(df.head())
    df.to_csv("../Datasets_forever/r_product_of.csv",index=False)

def preprocess_r_depict(file_path):
    def lafonctiondanslafonction(row):
        B = row["B"]
        index = B.find("une ")
        if "une " in B:
            row["B"] = B[4:]
            row["determinant"] = row["determinant"]+"une"
        else :
            if "un " in B:
                row["B"] = B[3:]
                row["determinant"] = row["determinant"]+"un"
        print(row)
        return row
    df = pd.read_csv(file_path)
    df.apply(lafonctiondanslafonction, axis=1)
    df.to_csv("../Datasets_forever/r_depict_new.csv",index=False)


def add_relation_tag(repertory_path,files_names):
    #files_names et une liste de nom de fichier (noms qui seront utilisés pour ajouter les relations)
    #repertory_path le chemin vers le repertoire qui contient les fichiers
    for fn in files_names:
        df = pd.read_csv(repertory_path+fn)
        df.insert(len(df.columns),"type_relation",[fn[:fn.index(".")]]*df.shape[0])
        df.to_csv(repertory_path+fn,index=False)


add_relation_tag("../Datasets_forever/",["r_depict.csv"])
#preprocess_r_depict("../Datasets_forever/r_depict.csv")
#preprocess_r_objet_matière("../Datasets_forever/r_product_of.csv")
#preprocess_topictxt("../Datasets_forever/r_topic.txt")