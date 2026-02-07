# 🔗 Mini projet : TALN 
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

La commande pour réaliser une inférence est :
```bash
cd genitif
python app.py
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