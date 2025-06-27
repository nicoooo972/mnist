# 🔧 Configuration GitHub pour nicoooo972/mnist

## 🎯 Repository: https://github.com/nicoooo972/mnist

### 1. **Permissions GitHub Actions**

Allez dans **Settings > Actions > General** :

```
☐ Actions permissions
  ✅ Allow all actions and reusable workflows

☐ Workflow permissions  
  ✅ Read and write permissions
  ✅ Allow GitHub Actions to create and approve pull requests
```

### 2. **Configuration Packages (Registry)**

Allez dans **Settings > Packages** :

```
☐ Package creation
  ✅ Enable improved container support

☐ Package visibility
  ✅ Inherit from repository (Public)
```

### 3. **Environments (Optionnel)**

Pour les déploiements automatiques, créez les environnements :

**Settings > Environments > New environment**

#### Environment: `staging`
```yaml
Environment name: staging
Deployment branches: develop
Required reviewers: (vide pour auto-deploy)
Environment secrets: (aucun requis)
```

#### Environment: `production`  
```yaml
Environment name: production
Deployment branches: Selected branches (tags v*)
Required reviewers: (optionnel - vous-même pour validation manuelle)
Environment secrets: (aucun requis)
```

### 4. **Vérification des Permissions Token**

Si vous rencontrez des problèmes de permissions :

1. Allez dans **Settings > Developer settings > Personal access tokens**
2. Créez un token avec ces permissions :
   ```
   ✅ repo (Full control of private repositories)
   ✅ write:packages (Upload packages to GitHub Package Registry)  
   ✅ read:packages (Download packages from GitHub Package Registry)
   ```

3. Ajoutez le token dans **Repository Settings > Secrets and variables > Actions** :
   ```
   Name: GITHUB_TOKEN_CUSTOM
   Value: votre_token_personnel
   ```

### 5. **Test de Configuration**

Commitez et poussez les fichiers de configuration :

```bash
git add .github/workflows/docker.yml
git add docker-compose.*.yml
git add deploy.sh
git add *.Dockerfile

git commit -m "🚀 Setup CI/CD pipeline"
git push origin main
```

Allez dans **Actions** pour vérifier que le workflow se lance.

---

## 🚀 Déploiement Initial

### **Option A: Via GitHub Actions (Auto)**

```bash
# 1. Entraîner le modèle localement
python train_model.py

# 2. Commit et push vers develop pour staging
git checkout -b develop
git add models/convnet.pt
git commit -m "➕ Add trained model"
git push origin develop

# → Le workflow build automatiquement les images
# → Deploy en staging sur http://localhost:8511
```

### **Option B: Manuel avec les Images du Registry**

Une fois les images buildées par GitHub Actions :

```bash
# Déploiement staging
./deploy.sh staging develop

# Déploiement production  
git tag v1.0.0
git push origin v1.0.0
./deploy.sh production v1.0.0
```

---

## 📦 Registry des Images

Vos images seront disponibles sur :

- **Frontend**: `ghcr.io/nicoooo972/mnist/mnist-frontend:latest`
- **Backend**: `ghcr.io/nicoooo972/mnist/mnist-backend:latest`

Les images sont publiques par défaut (selon les paramètres du repo).

---

## 🔍 URLs de Monitoring

### **GitHub**
- **Actions**: https://github.com/nicoooo972/mnist/actions
- **Packages**: https://github.com/nicoooo972/mnist/packages  
- **Releases**: https://github.com/nicoooo972/mnist/releases

### **Local (après déploiement)**
- **Frontend Staging**: http://localhost:8511
- **Backend Staging**: http://localhost:8010
- **Frontend Production**: http://localhost:8501
- **Backend Production**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ⚠️ Checklist Avant Premier Push

- [ ] Repository: https://github.com/nicoooo972/mnist configuré
- [ ] Permissions Actions: Read/Write ✅
- [ ] Packages activés ✅  
- [ ] Modèle entraîné: `models/convnet.pt` ✅
- [ ] Workflow présent: `.github/workflows/docker.yml` ✅
- [ ] Dockerfiles configurés ✅
- [ ] Deploy script exécutable: `chmod +x deploy.sh` ✅

---

## 🛠️ Commandes de Vérification

```bash
# Vérifier la structure
tree -L 3

# Vérifier les permissions
ls -la deploy.sh

# Test build local avant push
docker compose build

# Vérifier Git remote
git remote -v
# → origin  https://github.com/nicoooo972/mnist.git (fetch)
# → origin  https://github.com/nicoooo972/mnist.git (push)
``` 