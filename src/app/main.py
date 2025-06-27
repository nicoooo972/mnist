from fastapi import FastAPI, File, UploadFile
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import io
import sys
import os
import multiprocessing

# Désactiver le multiprocessing
multiprocessing.set_start_method('spawn', force=True)

# Définition du modèle ConvNet
class ConvNet(nn.Module):
    def __init__(self, input_size, n_kernels, output_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=n_kernels, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(in_channels=n_kernels, out_channels=n_kernels, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            nn.Flatten(),
            nn.Linear(in_features=n_kernels * 4 * 4, out_features=50),
            nn.ReLU(),
            nn.Linear(in_features=50, out_features=output_size)
        )
        
    def forward(self, x):
        return self.net(x)

app = FastAPI()

# Initialisation du modèle
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Charger le modèle avec ses paramètres
model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "convnet.pt")
if os.path.exists(model_path):
    checkpoint = torch.load(model_path, map_location=device)
    
    # Vérifier le format du modèle sauvegardé
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        # Nouveau format avec métadonnées
        n_kernels = checkpoint.get('n_kernels', 6)
        input_size = checkpoint.get('input_size', 1)
        output_size = checkpoint.get('output_size', 10)
        permutation = checkpoint.get('permutation', torch.randperm(784))
        
        model = ConvNet(input_size, n_kernels, output_size)
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        # Ancien format (juste les weights)
        print("Chargement d'un ancien modèle sans permutation sauvegardée")
        n_kernels = 6
        input_size = 1
        output_size = 10
        permutation = torch.randperm(784)  # Permutation aléatoire
        
        model = ConvNet(input_size, n_kernels, output_size)
        model.load_state_dict(checkpoint)
else:
    raise FileNotFoundError(
        f"❌ Aucun modèle entraîné trouvé à {model_path}!\n"
        f"🚀 Lancez d'abord: python train_model.py\n"
        f"📁 Le modèle sera sauvegardé dans models/convnet.pt"
    )

model.to(device)
model.eval()

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    # Convertir l'image en PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    # Convertir en niveaux de gris si nécessaire
    if image.mode != 'L':
        image = image.convert('L')
    # Redimensionner à 28x28
    image = image.resize((28, 28))
    
    # Convertir en numpy array et normaliser avec les paramètres MNIST
    image_array = np.array(image, dtype=np.float32) / 255.0
    # Inverser si nécessaire (MNIST a un fond noir)
    if image_array.mean() > 0.5:  # Si l'image est plus claire (fond blanc)
        image_array = 1.0 - image_array
    
    # Normalisation MNIST
    image_array = (image_array - 0.1307) / 0.3081
    
    # Convertir en tensor et appliquer la permutation
    image_tensor = torch.from_numpy(image_array.flatten())
    image_permuted = image_tensor[permutation]
    image_reshaped = image_permuted.view(1, 28, 28)
    
    return image_reshaped

def predict(image_tensor: torch.Tensor, model: torch.nn.Module) -> dict:
    # Ajouter la dimension batch
    image_tensor = image_tensor.unsqueeze(0).to(device)
    
    # Faire la prédiction
    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        predicted_class = torch.argmax(output, dim=1).item()
        confidence = probabilities[0][predicted_class].item()
    
    return {
        "predicted_class": int(predicted_class),
        "confidence": float(confidence),
        "probabilities": probabilities[0].cpu().numpy().tolist()
    }

@app.get("/")
async def root():
    return {"message": "API de classification MNIST", 
            "endpoints": {
                "predict": "/api/v1/predict",
                "docs": "/docs",
                "redoc": "/redoc"
            }}

@app.post("/api/v1/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    # Lire l'image
    image_bytes = await file.read()
    
    # Prétraiter l'image (retourne maintenant un tensor avec permutation)
    image_tensor = preprocess_image(image_bytes)
    
    # Faire la prédiction
    result = predict(image_tensor, model)
    
    return result
