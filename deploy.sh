#!/bin/bash

# 🚀 Script de déploiement MNIST Classifier
# Usage: ./deploy.sh [staging|production] [version]

set -e  # Exit on any error

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO=${GITHUB_REPOSITORY:-"nicoooo972/mnist"}
REGISTRY="ghcr.io"

# Fonction d'aide
usage() {
    echo "Usage: $0 [staging|production] [version]"
    echo ""
    echo "Exemples:"
    echo "  $0 staging develop        # Déploie la version develop en staging"
    echo "  $0 production v1.0.0      # Déploie la version v1.0.0 en production"
    echo "  $0 production latest      # Déploie la dernière version en production"
    exit 1
}

# Validation des arguments
if [ $# -lt 1 ]; then
    usage
fi

ENVIRONMENT=$1
VERSION=${2:-latest}

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}❌ Environnement invalide. Utilisez 'staging' ou 'production'${NC}"
    usage
fi

echo -e "${BLUE}🚀 Déploiement MNIST Classifier${NC}"
echo -e "${BLUE}📦 Environnement: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "${BLUE}🏷️  Version: ${YELLOW}$VERSION${NC}"
echo -e "${BLUE}📍 Registry: ${YELLOW}$REGISTRY/$GITHUB_REPO${NC}"
echo ""

# Vérification de Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé ou accessible${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé ou accessible${NC}"
    exit 1
fi

# Configuration des variables d'environnement
export GITHUB_REPOSITORY="$GITHUB_REPO"
export VERSION="$VERSION"

# Choix du fichier docker-compose
if [ "$ENVIRONMENT" = "staging" ]; then
    COMPOSE_FILE="docker-compose.staging.yml"
    FRONTEND_PORT="8511"
    BACKEND_PORT="8010"
else
    COMPOSE_FILE="docker-compose.prod.yml"
    FRONTEND_PORT="8501"
    BACKEND_PORT="8000"
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Fichier $COMPOSE_FILE introuvable${NC}"
    exit 1
fi

echo -e "${YELLOW}📥 Téléchargement des images Docker...${NC}"

# Pull des images
docker pull "$REGISTRY/$GITHUB_REPO/mnist-frontend:$VERSION" || {
    echo -e "${RED}❌ Impossible de télécharger l'image frontend${NC}"
    exit 1
}

docker pull "$REGISTRY/$GITHUB_REPO/mnist-backend:$VERSION" || {
    echo -e "${RED}❌ Impossible de télécharger l'image backend${NC}"
    exit 1
}

echo -e "${GREEN}✅ Images téléchargées avec succès${NC}"

# Vérification du modèle
if [ ! -d "./models" ] || [ ! -f "./models/convnet.pt" ]; then
    echo -e "${YELLOW}⚠️  Aucun modèle trouvé dans ./models/convnet.pt${NC}"
    echo -e "${YELLOW}🏃 Exécutez d'abord: python train_model.py${NC}"
    
    read -p "Continuer sans modèle ? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${YELLOW}🔄 Arrêt des conteneurs existants...${NC}"
docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true

echo -e "${YELLOW}🚀 Démarrage des nouveaux conteneurs...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Attendre que les services soient prêts
echo -e "${YELLOW}⏳ Attente du démarrage des services...${NC}"
sleep 10

# Vérification de la santé des services
echo -e "${YELLOW}🔍 Vérification de l'état des services...${NC}"

# Backend
if curl -f "http://localhost:$BACKEND_PORT/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend opérationnel sur le port $BACKEND_PORT${NC}"
else
    echo -e "${RED}❌ Backend non accessible sur le port $BACKEND_PORT${NC}"
fi

# Frontend  
if curl -f "http://localhost:$FRONTEND_PORT/_stcore/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend opérationnel sur le port $FRONTEND_PORT${NC}"
else
    echo -e "${RED}❌ Frontend non accessible sur le port $FRONTEND_PORT${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Déploiement terminé !${NC}"
echo ""
echo -e "${BLUE}📱 URLs d'accès:${NC}"
echo -e "  🌐 Frontend: ${YELLOW}http://localhost:$FRONTEND_PORT${NC}"
echo -e "  🔧 Backend:  ${YELLOW}http://localhost:$BACKEND_PORT${NC}"
echo -e "  📚 API Docs: ${YELLOW}http://localhost:$BACKEND_PORT/docs${NC}"
echo ""
echo -e "${BLUE}📋 Commandes utiles:${NC}"
echo -e "  📊 Logs:        ${YELLOW}docker-compose -f $COMPOSE_FILE logs -f${NC}"
echo -e "  📈 Statut:      ${YELLOW}docker-compose -f $COMPOSE_FILE ps${NC}"
echo -e "  🛑 Arrêt:       ${YELLOW}docker-compose -f $COMPOSE_FILE down${NC}"
echo -e "  🔄 Redémarrage: ${YELLOW}docker-compose -f $COMPOSE_FILE restart${NC}"

# Affichage des logs en temps réel (optionnel)
read -p "Voulez-vous voir les logs en temps réel ? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📋 Logs en temps réel (Ctrl+C pour quitter):${NC}"
    docker-compose -f "$COMPOSE_FILE" logs -f
fi 