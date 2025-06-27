FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/

# Créer le dossier models 
RUN mkdir -p ./models

# Copier les modèles s'ils existent, sinon créer un fichier vide
COPY models/ ./models/
RUN touch ./models/.gitkeep 2>/dev/null || true

# Définir le PYTHONPATH pour que les imports fonctionnent
ENV PYTHONPATH=/app/src

# Exposer le port
EXPOSE 8000

# Variable d'environnement pour désactiver le buffering
ENV PYTHONUNBUFFERED=1

# Commande pour lancer l'API
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 