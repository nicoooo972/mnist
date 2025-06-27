# 🚀 Guide de Démarrage Rapide - CI/CD

## ⚡ Mise en Place en 5 Minutes

### 1. **Setup GitHub Repository**
```bash
# Clonez votre repo
git clone https://github.com/votre-username/votre-repo.git
cd votre-repo

# Assurez-vous d'avoir les bons fichiers
ls -la .github/workflows/docker.yml    # ✅ Workflow CI/CD
ls -la docker-compose.*.yml            # ✅ Configs déploiement
ls -la deploy.sh                       # ✅ Script déploiement
```

### 2. **Configuration GitHub**
Dans **Settings > Actions > General** :
- ✅ Enable "Read and write permissions" 
- ✅ Allow GitHub Actions to create releases

Dans **Settings > Packages** :
- ✅ Enable "Improved container support"

### 3. **Premier Déploiement**

#### Option A : Via GitHub Actions (Recommandé)
```bash
# Entraîner le modèle en local
python train_model.py

# Commit et push vers develop
git add .
git commit -m "🚀 Initial deployment setup"
git push origin develop
```

#### Option B : Déploiement Manuel
```bash
# Entraîner le modèle
python train_model.py

# Déployer en staging
./deploy.sh staging develop
```

---

## 🔄 Workflows de Développement

### **Développement Feature**
```bash
# 1. Créer une feature branch
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer votre fonctionnalité
# ... modifications ...

# 3. Push et créer PR vers main
git push origin feature/nouvelle-fonctionnalite
# → GitHub Actions lance tests automatiques
```

### **Staging Release**
```bash
# 1. Merger PR dans develop
git checkout develop
git merge feature/nouvelle-fonctionnalite
git push origin develop

# → Auto-deploy en staging !
# → Images: ghcr.io/owner/repo/mnist-*:develop  
# → URL: http://localhost:8511
```

### **Production Release**
```bash
# 1. Créer un tag de version
git tag v1.0.0
git push origin v1.0.0

# → Auto-deploy en production !
# → Images: ghcr.io/owner/repo/mnist-*:v1.0.0
# → URL: http://localhost:8501
# → Création GitHub Release automatique
```

---

## 🐳 Commandes Docker Essentielles

### **Développement Local**
```bash
# Build et run local
docker compose up --build

# Logs en temps réel
docker compose logs -f

# Redémarrage propre
docker compose down && docker compose up -d
```

### **Déploiement Staging**
```bash
# Via script (recommandé)
./deploy.sh staging develop

# Via docker-compose direct
export GITHUB_REPOSITORY="owner/repo"
export VERSION="develop"
docker-compose -f docker-compose.staging.yml up -d
```

### **Déploiement Production**
```bash
# Via script (recommandé)
./deploy.sh production v1.0.0

# Via docker-compose direct  
export GITHUB_REPOSITORY="owner/repo"
export VERSION="v1.0.0"
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔍 Monitoring & Debug

### **Vérifier l'État des Services**
```bash
# Status containers
docker ps

# Health checks
curl http://localhost:8000/          # Backend health
curl http://localhost:8501/_stcore/health  # Frontend health

# Logs détaillés
docker logs mnist-backend-prod
docker logs mnist-frontend-prod
```

### **GitHub Actions Debug**
1. **Actions tab** dans votre repo GitHub
2. Cliquez sur le workflow en cours/échoué
3. Regardez les logs de chaque job
4. **Re-run failed jobs** si nécessaire

### **Registry GitHub**
Vos images sont visibles dans :
- **Packages tab** de votre repo
- `ghcr.io/owner/repo` (public)

---

## 🚨 Dépannage Courant

### **Problème : "Permission denied" lors du push d'images**
```bash
# Solution : Vérifier les permissions GitHub
# Repository Settings > Actions > General
# ✅ "Read and write permissions"
```

### **Problème : Images non trouvées lors du déploiement**
```bash
# Vérifier que les images existent
docker pull ghcr.io/owner/repo/mnist-frontend:develop

# Vérifier les variables d'environnement
echo $GITHUB_REPOSITORY
echo $VERSION
```

### **Problème : API non accessible**
```bash
# Vérifier que le modèle existe
ls -la models/convnet.pt

# Re-entraîner si nécessaire
python train_model.py

# Redémarrer les containers
./deploy.sh production latest
```

### **Problème : Workflow GitHub Actions échoue**
```bash
# Vérifier les secrets (si nécessaires)
# Settings > Secrets and variables > Actions

# Vérifier les permissions packages
# Settings > Developer settings > Personal access tokens
# ✅ write:packages, read:packages
```

---

## 🎯 Checklist de Déploiement

### **Avant le Premier Push**
- [ ] Modèle entraîné (`models/convnet.pt` existe)
- [ ] Tests locaux réussis (`docker compose up`)
- [ ] Workflow GitHub Actions présent (`.github/workflows/docker.yml`)
- [ ] Permissions GitHub configurées

### **Avant un Déploiement Production**  
- [ ] Tests en staging réussis
- [ ] Code review terminée
- [ ] Version taguée (`git tag v1.x.x`)
- [ ] Scan sécurité passé
- [ ] Documentation mise à jour

### **Après un Déploiement**
- [ ] Services accessibles (frontend + backend)
- [ ] API répond correctement
- [ ] Logs sans erreurs critiques
- [ ] Performance acceptable
- [ ] Monitoring opérationnel

---

## 📚 Liens Utiles

- **Logs GitHub Actions** : `https://github.com/owner/repo/actions`
- **Registry Images** : `https://github.com/owner/repo/packages`
- **Releases** : `https://github.com/owner/repo/releases`
- **Documentation Docker** : `README_DOCKER.md`
- **API Documentation** : `http://localhost:8000/docs` (quand actif) 