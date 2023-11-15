import pandas as pd
import re

# Chargement du fichier CSV
file_path = 'backend/data/cookie_training.csv'
cookie_data = pd.read_csv(file_path)

# Constantes pour les catégories
SECURITY = 'Sécurité'
AD_TRACKING = 'Suivi/Publicité'
FUNCTIONAL = 'Fonctionnel'
PERSISTENT = 'Persistant'
STATISTICS_ANALYTICS = 'Statistiques/Analytiques'
UNCLASSIFIED = 'Non classifié'

def classify_cookie(row):
    # Classification basée sur les attributs de sécurité
    http_only = row.get('HTTP Only')
    secure = row.get('Sécurisé')
    if http_only == 'True' or secure == 'True':
        return SECURITY

    # Classification basée sur la durée de vie
    lifetime = row.get('Durée de Vie')
    if lifetime == 'Tierce Partie':
        return AD_TRACKING

    # Classification basée sur le chemin
    path = row.get('Chemin')
    if path == 'Session':
        return FUNCTIONAL
    elif path == 'Persistent':
        return PERSISTENT

    # Classification basée sur le nom du cookie
    name = str(row.get('Nom du cookie', '')).lower()
    if re.search(r"(_ga|_gid|analytics|_utma|_utmz)", name):
        return STATISTICS_ANALYTICS

    return UNCLASSIFIED

# Application de la fonction de classification à chaque ligne
cookie_data['Catégorie'] = cookie_data.apply(classify_cookie, axis=1)

# Enregistrement des données classifiées dans un nouveau fichier CSV
cookie_data.to_csv('backend/data/classified_cookies_V2.csv', index=False)
