# 🔗 Mini projet : TALN 2
Hugo SILIVERI - Lucien BOUBY

## 📂 Structure du projet

Le projet contiens deux dossiers :

- **`dataset/`** : Les datasets utilisés pour l'entrainement du modèle
- **`Models/`** : Le code et les modèles entrainés

## 🐍  Python

### 📄 Description des fichiers

- **`app.py`** : Fichier central de l'application à exécuter
- **`predict.py`** : Regroupe les méthodes pour faire les prédictions
- **`train.py`** : Regroupe des méthodes utiles pour l'entrainement
- **`vectorizer.py`** : Regroupe des méthodes utiles pour vectoriser les datasets
- **`Models/Tree.py`** : Regroupe des méthodes utiles pour la construction du modèle

### ▶️ Exécution de l'application

Lancer les conteneurs Docker :
```bash
docker compose up -d --build
```

Pour accéder au shell du conteneur de l'application :
```bash
docker exec -it app_container sh
```

Les commandes pour lancer l'application sont :
```bash
cd genitif
python app.py
```

Vous aurez ensuite une boite de dialogue avec ces choix où il faut répondre 'o' pour oui et 'n' pour non selon ce que vous voulez faire : 

```text
[1] Lancer le nettoyage des datasets ? (o/n) : #Fonction qui servait à rajouter le type de relation pour chaque triplet du dataset
[2] Lancer la vectorisation ? (o/n) :
[3] Lancer l'entrainement du modèle ? (o/n) :
[4] Lancer le K-Fold lors de l'entrainement ? (o/n) : 
[5] Lancer la prédiction ? (o/n) : 
```


## ❓ FAQ

### 🛑 Comment arrêter les conteneurs Docker ?
```bash
docker compose down
```

### ♻️ Comment reset les conteneurs Docker ?
```bash
docker rm $(docker ps -a -q)
```

### 🔍 Comment accéder à la base de données Redis ?
Il faut exécuter les commandes : 
```bash
docker exec -it redis_container sh
redis-cli
```