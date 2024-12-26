import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


# Spécifiez le chemin du driver
driver_path = "./chromedriver"  # Assurez-vous que 'chromedriver' est dans le bon dossier

# Utilisez la classe Service pour définir le chemin du WebDriver
service = Service(driver_path)

BASE_URL = "http://127.0.0.1:8000"  

def api_login(email, password):
    """
    Authentifie l'utilisateur via l'API `login/` et retourne le token d'accès.
    """
    response = requests.post(f"{BASE_URL}/accounts/login/", json={
        "email": email,
        "password": password
    })
    response.raise_for_status()
    access_token = response.json().get("access")
    if not access_token:
        raise ValueError("Token d'accès non trouvé dans la réponse.")
    return access_token


def api_create_user_patient(access_token):
    """
    Crée un compte user patient via l'API et retourne son ID.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{BASE_URL}/accounts/register/", headers=headers, json={
        "email": "test258@gmail.com",
        "password":"test",
        "role": "patient"
    })
    response.raise_for_status()
    
    return response.json()["id"]

def api_create_patient(access_token, user_id):
    """
    Crée un patient via l'API et retourne son ID.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{BASE_URL}/accounts/patient/", headers=headers, json={
        "nom": "Test",
        "prenom": "Patient",
        "date_naissance": "2000-01-01",
        "adresse": "123 Rue Test",
        "tel": "0123456789",
        "adresse":"bejaia",
        "mutuelle":"sante",
        "medecin_traitant_id":1,
        "personne_a_contacter":"sarah",
        "nss":"2777779875",
        "user_id":user_id
    })
    response.raise_for_status()
    return response.json()["id"]


def test_create_dpi_with_selenium():
    """
    Test fonctionnel : création d'un DPI après préparation des données via les APIs.
    """
    email = "medecin5@gmail.com"
    password = "sarah"

    # Étape 1 : Authentification via l'API
    access_token = api_login(email, password)
    
    # Étape 2 : Création d'un compte user patient via l'API
    user_id = api_create_user_patient(access_token)
    
    # Étape 3 : Création d'un patient via l'API
    patient_id = api_create_patient(access_token, user_id)

    # Initialiser Selenium WebDriver
    driver = webdriver.Chrome(service=service)  
    try:
        # Étape 4 : Accéder à l'interface de création du DPI
        driver.get(BASE_URL)  # Charger la page principale
        driver.add_cookie({"name": "access_token", "value": access_token})  # Ajouter le token d'accès comme cookie

        # Recharger la page pour appliquer le cookie
        driver.refresh()

        # Accéder au formulaire de création du DPI
        driver.get(f"{BASE_URL}/create-dpi/")  # URL mise à jour ici

        # Étape 5 : Remplir le formulaire
        patient_id_input = driver.find_element(By.NAME, "patient_id")
        patient_id_input.send_keys(str(patient_id))

        
        submit_button = driver.find_element(By.TAG_NAME, "button")
        submit_button.click()

        # Étape 6 : Vérification des résultats
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Dossier créé avec succès" in success_message.text, "Échec de la création du DPI."

    finally:
        # Nettoyage : Fermer le navigateur
        driver.quit()

if __name__ == "__main__":
    test_create_dpi_with_selenium()
