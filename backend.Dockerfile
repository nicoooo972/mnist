FROM python:3.11-slim

# Métadonnées pour le registry
LABEL org.opencontainers.image.title="MNIST Classifier Backend"
LABEL org.opencontainers.image.description="FastAPI backend for MNIST digit classification"
LABEL org.opencontainers.image.source="https://github.com/nicoooo972/mnist"
LABEL org.opencontainers.image.licenses="MIT"

# Définir le répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/

# Créer le dossier models et copier les modèles
RUN mkdir -p ./models
COPY models ./models

# Définir le PYTHONPATH pour que les imports fonctionnent
ENV PYTHONPATH=/app/src

# Variable d'environnement pour désactiver le buffering
ENV PYTHONUNBUFFERED=1

# Utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Exposer le port
EXPOSE 8000

# Commande pour lancer l'API
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 