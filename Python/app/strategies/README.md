# 🔗 Mini projet : Inférences

Hugo SILIVERI - Lucien BOUBY

## 📂 Structure du projet

Le projet est organisé en deux dossiers principaux :

- **`Python/`** : Contient l'application et le `Dockerfile`
- **`Redis/`** : Généré lors de l'exécution du fichier `docker-compose.yml` et stocke les données du cache


## 🐍  Python

### 📄 Description des fichiers

- **`app.py`** : Fichier central de l'application à exécuter pour trouver les inférences
- **`api.py`** : Regroupe les méthodes pour communiquer avec l'API de JeuxDeMots et la mise en cache des réponses
- **`utils.py`** : Regroupe des méthodes utiles au fonctionnement de l'application
- **`relations.json`** : Liste des relations avec leurs identifiants

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
cd strategies
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