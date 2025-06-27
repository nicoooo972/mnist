FROM python:3.11-slim

# Métadonnées pour le registry
LABEL org.opencontainers.image.title="MNIST Classifier Frontend"
LABEL org.opencontainers.image.description="Streamlit frontend for MNIST digit classification"
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

# Copier l'application Streamlit
COPY src/app/streamlit_app.py ./

# Configuration Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Exposer le port Streamlit
EXPOSE 8501

# Variable d'environnement pour désactiver le buffering
ENV PYTHONUNBUFFERED=1

# Commande pour lancer Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 