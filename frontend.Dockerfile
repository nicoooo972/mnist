FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application Streamlit
COPY src/app/streamlit_app.py ./

# Exposer le port Streamlit
EXPOSE 8501

# Variable d'environnement pour désactiver le buffering
ENV PYTHONUNBUFFERED=1

# Configuration Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Commande pour lancer Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 