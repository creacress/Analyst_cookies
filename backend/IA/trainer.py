import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
import signal
from torch.utils.data import TensorDataset, DataLoader

# Vérification de la disponibilité de MPS et définition du device
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
print(f"Utilisation de {device} pour l'entraînement.")

# Fonction pour gérer l'interruption et sauvegarder le modèle
def save_model_on_interrupt(model, filepath):
    def handler(signum, frame):
        print("🔴 Oh non ! Une interruption sauvage apparaît !")
        print("🔥 Sauvegarde du modèle en cours... Ne bougez pas !")
        torch.save(model.state_dict(), filepath)
        print(f"🎉 Modèle sauvegardé avec succès dans '{filepath}'. À bientôt !")
        exit(0)
    return handler

# Chemin pour sauvegarder le modèle
model_save_path = 'mon_modele.pth'

# Chemins des fichiers de tenseurs
X_train_file_path = 'backend/data/X_train_tensor.pt'  # Assurez-vous que ce chemin est correct
y_train_file_path = 'backend/data/y_train_tensor.pt'  # Assurez-vous que ce chemin est correct

# Chargement des tenseurs
X_train = torch.load(X_train_file_path)
y_train = torch.load(y_train_file_path)

# Si vous avez des données de test séparées, chargez-les ici de la même manière
X_test_file_path = 'backend/data/X_test_tensor.pt'
y_test_file_path = 'backend/data/y_test_tensor.pt'
X_test = torch.load(X_test_file_path)
y_test = torch.load(y_test_file_path)

# Séparation des caractéristiques et des étiquettes
# Convertir explicitement en float32
# X_train = torch.tensor(train_data.drop('Catégorie', axis=1).values, dtype=torch.float32)
# y_train = torch.tensor(train_data['Catégorie'].values, dtype=torch.long)
# X_test = torch.tensor(test_data.drop('Catégorie', axis=1).values, dtype=torch.float32)
# y_test = torch.tensor(test_data['Catégorie'].values, dtype=torch.long)

# Normalisation des données
scaler = StandardScaler()
X_train = torch.tensor(scaler.fit_transform(X_train), dtype=torch.float32)
X_test = torch.tensor(scaler.transform(X_test), dtype=torch.float32)

class EnhancedNet(nn.Module):
    def __init__(self, num_features, num_classes):
        super(EnhancedNet, self).__init__()
        self.fc1 = nn.Linear(num_features, 1920)
        self.bn1 = nn.BatchNorm1d(1920)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(1920, 1920)
        self.bn2 = nn.BatchNorm1d(1920)
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(1920, num_classes)

    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = self.fc3(x)
        return x

num_features = X_train.shape[1]
num_classes = len(y_train.unique())
model = EnhancedNet(num_features, num_classes).to(device)


# Compilation du modèle
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Préparation des données pour PyTorch
train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)

# Configuration du gestionnaire d'interruption
signal.signal(signal.SIGINT, save_model_on_interrupt(model, model_save_path))

# Entraînement du modèle
print("💪 Entraînement en cours... Allez, on pousse !")
model.train()
for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

# Évaluation du modèle
print("🎯 Entraînement terminé. Passons à l'évaluation...")
model.eval()
with torch.no_grad():
    # Préparation des données de test pour PyTorch
    test_dataset = TensorDataset(X_test, y_test)
    test_loader = DataLoader(test_dataset, batch_size=8)

    correct = 0
    total = 0
    for data, target in test_loader:
        data, target = data.to(device), target.to(device)
        outputs = model(data)
        _, predicted = torch.max(outputs.data, 1)
        total += target.size(0)
        correct += (predicted == target).sum().item()

accuracy = 100 * correct / total
print(f"Précision du modèle sur l'ensemble de test: {accuracy:.2f}%")
