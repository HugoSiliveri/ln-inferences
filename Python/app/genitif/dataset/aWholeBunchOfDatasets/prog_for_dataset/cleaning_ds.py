import re
import os
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


def add_relation_tag(repertory_path, files_names):
    for fn in files_names:
        file_path = os.path.join(repertory_path, fn)
        df = pd.read_csv(file_path)

        if "type_relation" in df.columns:
            df = df.drop(columns=["type_relation"])

        base_name = fn[:fn.index(".")]
        if base_name == "r_objet_matière":
            tag = "r_objet>matière"
        elif base_name == "r_lieu_origine":
            tag = "r_lieu>origine"
        elif base_name == "r_processus_instr-1":
            tag = "r_processus>instr-1"
        else:
            tag = base_name

        df.insert(len(df.columns), "type_relation", [tag] * df.shape[0])
        df.to_csv(file_path, index=False)

#add_relation_tag("../Datasets_forever/",["r_depict.csv"])
#preprocess_r_depict("../Datasets_forever/r_depict.csv")
#preprocess_r_objet_matière("../Datasets_forever/r_product_of.csv")
#preprocess_topictxt("../Datasets_forever/r_topic.txt")