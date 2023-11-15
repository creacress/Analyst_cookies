from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import torch

# Modification du code pour inclure la division en ensembles d'entraînement et de test (80% / 20%)

# Chargement des données depuis le fichier CSV
cookies_data = pd.read_csv("backend/data/classified_cookies_V2.csv")

# Séparation des données en colonnes et nettoyage
cookies_data = cookies_data['Nom du cookie;Domaine;Chemin;Durée de Vie;HTTP Only;Sécurisé;SameSite;Catégorie'].str.split(';', expand=True)
cookies_data.columns = ['Nom du cookie', 'Domaine', 'Chemin', 'Durée de Vie', 'HTTP Only', 'Sécurisé', 'SameSite', 'Catégorie']
cookies_data.replace("", float("NaN"), inplace=True)
cookies_data.dropna(how='all', inplace=True)
cookies_data['HTTP Only'] = cookies_data['HTTP Only'].map({'True': 1, 'False': 0})
cookies_data['Sécurisé'] = cookies_data['Sécurisé'].map({'True': 1, 'False': 0})

# Encodage des caractéristiques catégorielles
label_encoder = LabelEncoder()
categorical_columns = ['Domaine', 'Chemin', 'Durée de Vie', 'SameSite', 'Catégorie']
for col in categorical_columns:
    cookies_data[col] = label_encoder.fit_transform(cookies_data[col])

# Séparation des caractéristiques et des étiquettes
X = cookies_data.drop(['Nom du cookie', 'Catégorie'], axis=1)
y = cookies_data['Catégorie']

# Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Conversion des DataFrame Pandas en tenseurs PyTorch pour l'entraînement et le test
X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)
X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.long)

# Sauvegarde des tenseurs en fichiers .pt
torch.save(X_train_tensor, 'backend/data/X_train_tensor.pt')
torch.save(y_train_tensor, 'backend/data/y_train_tensor.pt')
torch.save(X_test_tensor, 'backend/data/X_test_tensor.pt')
torch.save(y_test_tensor, 'backend/data/y_test_tensor.pt')

# Renvoi des chemins des fichiers sauvegardés
('backend/data/X_train_tensor.pt', 'backend/data/y_train_tensor.pt', 'backend/data/X_test_tensor.pt', 'backend/data/y_test_tensor.pt')
