# 🐳 Guide Docker - Classification MNIST

## Architecture

L'application est divisée en 2 conteneurs :
- **Backend** : API FastAPI (port 8000)
- **Frontend** : Interface Streamlit (port 8501)

## Prérequis

1. **Docker et Docker Compose** installés
2. **Modèle entraîné** dans le dossier `models/`

## Entraîner le modèle

Avant de lancer les conteneurs, il faut entraîner le modèle :

```bash
python train_model.py
```

Cela créé `models/convnet.pt` avec la permutation sauvegardée.

## Lancement avec Docker Compose

### 🚀 Démarrage complet

```bash
# Construire et lancer les 2 services
docker-compose up --build

# En arrière-plan
docker-compose up --build -d
```

### 📊 Accès aux interfaces

- **Frontend Streamlit** : http://localhost:8501
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

### 🛠️ Commandes utiles

```bash
# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Supprimer les images
docker-compose down --rmi all

# Rebuild seulement le frontend
docker-compose build frontend

# Restart seulement le backend  
docker-compose restart backend
```

## Structure des fichiers

```
├── backend.Dockerfile      # Image FastAPI
├── frontend.Dockerfile     # Image Streamlit
├── docker-compose.yml      # Orchestration
├── .dockerignore           # Fichiers exclus
├── requirements.txt        # Dépendances Python
├── src/
│   └── app/
│       ├── main.py         # API FastAPI
│       └── streamlit_app.py # Interface Streamlit
├── models/
│   └── convnet.pt          # Modèle entraîné
└── train_model.py          # Script d'entraînement
```

## Variables d'environnement

- `API_URL` : URL de l'API backend (définie automatiquement dans docker-compose)

## Résolution de problèmes

### API ne démarre pas
```bash
# Vérifier que le modèle existe
ls -la models/

# Si absent, entraîner
python train_model.py
```

### Streamlit ne peut pas contacter l'API
```bash
# Vérifier que le backend est démarré
docker-compose ps

# Vérifier les logs
docker-compose logs backend
```

### Reconstruction complète
```bash
# Nettoyer et reconstruire
docker-compose down --rmi all
docker-compose up --build
``` 