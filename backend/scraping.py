import os
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def extract_cookies(url):
    # Configuration du WebDriver
    options = Options()
    options.headless = True  # Exécution en mode sans tête
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Attendre que le bouton de consentement des cookies soit cliquable
    wait = WebDriverWait(driver, 10)
    cookie_button_xpath = (
    "//button[" 
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'fermer') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"j'accepte\") or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'consentir') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continuer') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'valider') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i agree') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'consent') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'allow') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept all cookies') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter & fermer') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter et fermer') or "
    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter les cookies')"
    "]"
)



    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, cookie_button_xpath))).click()
    except TimeoutException:
        print("Pas de fenêtre de consentement des cookies détectée ou délai dépassé.")
    except Exception as e:
        print(f"Une erreur est survenue: {e}")


    cookies = driver.get_cookies()
    driver.quit()
    return cookies

def classify_cookie_by_lifetime(cookie):
    if 'expiry' in cookie:
        return 'Persistent' # Cookies avec une date d'expiration définie.
    else:
        return 'Session' # Cookies qui expirent à la fin de la session de navigation.

def classify_cookie_by_domain(cookie):
    if cookie['domain'].startswith('.'):
        return 'Tierce Partie'
    else:
        return 'Première-Partie'

def classify_cookie_by_security(cookie):
    classifications = []
    if cookie.get('httpOnly'):
        classifications.append('HttpOnly')
    if cookie.get('secure'):
        classifications.append('Secure')
    return classifications if classifications else ['None']

def classify_cookie_by_purpose(cookie):
    # Cette fonction nécessiterait une logique plus complexe basée sur le nom du cookie,
    # ses valeurs ou d'autres heuristiques. Pour l'exemple, cette fonction renvoie 'Unknown'.
    return 'Unknown'

def analyze_cookies(cookies):
    report = []
    for cookie in cookies:
        cookie_report = {
            'Name': cookie['name'],
            'Domain': cookie['domain'],
            'Lifetime': classify_cookie_by_lifetime(cookie),
            'Domain Type': classify_cookie_by_domain(cookie),
            'Security': classify_cookie_by_security(cookie),
            'Purpose': classify_cookie_by_purpose(cookie),
            'HttpOnly': cookie.get('httpOnly', False),
            'Secure': cookie.get('secure', False),
            'Expiration': datetime.datetime.fromtimestamp(cookie['expiry']).strftime('%Y-%m-%d %H:%M:%S') if 'expiry' in cookie else 'Session',
        }
        report.append(cookie_report)
    return report

def save_to_csv(cookies, file_path):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Écrire les en-têtes de colonnes uniquement si le fichier est nouveau
            writer.writerow(['Name', 'Domain', 'Lifetime', 'Domain Type', 'Security', 'Purpose', 'HttpOnly', 'Secure', 'Expiration'])
        for cookie in cookies:
            writer.writerow([
                cookie['Name'], 
                cookie['Domain'], 
                cookie['Lifetime'], 
                cookie['Domain Type'], 
                '; '.join(cookie['Security']), 
                cookie['Purpose'], 
                cookie['HttpOnly'], 
                cookie['Secure'], 
                cookie['Expiration']
            ])

# Test de la fonction extract_cookies
test_url = "https://instagram.com/"
test_cookies = extract_cookies(test_url)


# Analyse des cookies extraits
report = analyze_cookies(test_cookies)

# Enregistrement des cookies dans un fichier CSV
save_to_csv(report, 'backend/data/cookie_training.csv')
