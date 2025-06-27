import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
import os

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

# Fonction d'entraînement
def train_model(model, train_loader, device, perm=None, n_epoch=1):
    if perm is None:
        perm = torch.randperm(784)

    perm = perm.to(device)
    model.to(device)
    model.train()

    optimizer = torch.optim.AdamW(model.parameters())

    for epoch in range(n_epoch):
        print(f"--- Epoch {epoch+1}/{n_epoch} ---")
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            batch_size = data.shape[0]
            data_flattened = data.view(batch_size, -1)
        
            if data_flattened.shape[1] != perm.shape[0]:
                raise ValueError(f"La dimension des données aplaties ({data_flattened.shape[1]}) "
                                f"ne correspond pas à la taille de la permutation ({perm.shape[0]}). "
                                f"Assurez-vous que l'image est bien 28x28 ou ajustez 'perm'.")
        
            data_permuted = data_flattened[:, perm]
            data_reshaped = data_permuted.view(batch_size, 1, 28, 28)
            
            optimizer.zero_grad()
            logits = model(data_reshaped)
            
            loss = F.cross_entropy(logits, target)

            loss.backward()
            optimizer.step()

            if batch_idx % 100 == 0:
                print(f"  Epoch: {epoch+1}/{n_epoch} | Batch (Step): {batch_idx}/{len(train_loader)} | Loss: {loss.item():.4f}")

        print(f"--- Fin de l'Epoch {epoch+1} ---")

# Fonction de test
def test_model(model, test_loader, device, perm=None):
    if perm is None:
        perm = torch.randperm(784)

    perm = perm.to(device)
    model.to(device)
    model.eval()
    test_loss = 0
    correct = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            batch_size = data.shape[0]
            data_flattened = data.view(batch_size, -1)
        
            if data_flattened.shape[1] != perm.shape[0]:
                raise ValueError(f"La dimension des données aplaties ({data_flattened.shape[1]}) "
                                f"ne correspond pas à la taille de la permutation ({perm.shape[0]}). "
                                f"Assurez-vous que l'image est bien 28x28 ou ajustez 'perm'.")
            
            data_permuted = data_flattened[:, perm]
            data_reshaped = data_permuted.view(batch_size, 1, 28, 28)
            
            logits = model(data_reshaped)
            test_loss += F.cross_entropy(logits, target, reduction='sum').item()
        
            pred = torch.argmax(logits, dim=1)
            correct += pred.eq(target.view_as(pred)).sum().item()
        
        test_loss /= len(test_loader.dataset)
        accuracy = 100. * correct / len(test_loader.dataset)
        print(f'\nTest set: Average loss: {test_loss:.4f}, Accuracy: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)\n')
        return test_loss, accuracy

def main():
    # Configuration du device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    # Chargement des données
    tf = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST("../data/raw", download=True, train=True, transform=tf),
        batch_size=64, shuffle=True
    )
    
    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST("../data/raw", download=True, train=False, transform=tf),
        batch_size=64, shuffle=True
    )

    # Paramètres du modèle
    n_kernels = 6
    input_size = 1
    output_size = 10

    # Création d'une permutation unique pour entraînement et test
    perm = torch.randperm(784)

    # Création et entraînement du modèle
    convnet = ConvNet(input_size, n_kernels, output_size)
    convnet.to(device)
    print(f"Parameters={sum(p.numel() for p in convnet.parameters())/1e3}K")
    
    # Entraînement
    train_model(convnet, train_loader, device, perm)
    
    # Test
    test_model(convnet, test_loader, device, perm)

    # Sauvegarde du modèle avec la permutation
    os.makedirs("../models", exist_ok=True)
    
    # Sauvegarder le modèle et la permutation utilisée
    model_data = {
        'model_state_dict': convnet.state_dict(),
        'permutation': perm,
        'n_kernels': n_kernels,
        'input_size': input_size,
        'output_size': output_size
    }
    torch.save(model_data, "../models/convnet.pt")

if __name__ == "__main__":
    main()