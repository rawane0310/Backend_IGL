from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service

# Spécifiez le chemin du driver
driver_path = "./chromedriver.exe"

# Utilisez la classe Service pour définir le chemin du WebDriver
service = Service(driver_path)

BASE_URL = "http://127.0.0.1:8000"


def test_create_dpi():
    # Initialiser le WebDriver (assurez-vous que ChromeDriver est installé)
    driver = webdriver.Chrome(service=service)

    try:
        # Étape 1 : Connexion
        print("Accéder à la page de connexion...")
        driver.get(f"{BASE_URL}/accounts/loginTest/")
        driver.find_element(By.NAME, "email").send_keys("medecin5@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("sarah")
        driver.find_element(By.TAG_NAME, "button").click()

        # Attendre la réponse
        time.sleep(1)
        assert "Login successful" in driver.page_source

        role_user="medecin"
        roles_autorisés=["medecin","administratif"]

        #verifier si le role de l'utilisateur l'autorise à creer un compte patient
        if role_user not in roles_autorisés:
            print("Rôle non autorisé. Fin du programme.")
            driver.quit()  # Fermer le navigateur proprement
            exit()  # Quitter le programme

        # Étape 2 : Créer un compte patient
        print("Création du compte patient...")
        driver.get(f"{BASE_URL}/accounts/create-account/")
        driver.find_element(By.NAME, "email").send_keys("test@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("sarah")
        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(1)
        assert "Account created" in driver.page_source

        # Étape 3 : Créer un profil patient
        print("Création du profil patient...")
        driver.get(f"{BASE_URL}/accounts/create-profile/")
        driver.find_element(By.NAME, "nom").send_keys("Dupont")
        driver.find_element(By.NAME, "prenom").send_keys("Jean")
        driver.find_element(By.NAME, "date_naissance").send_keys("2004-10-03")
        driver.find_element(By.NAME, "adresse").send_keys("123 rue de Paris")
        driver.find_element(By.NAME, "tel").send_keys("000479")
        driver.find_element(By.NAME, "mutuelle").send_keys("sante")
        driver.find_element(By.NAME, "medecin_traitant_email").send_keys("medecin5@gmail.com")
        driver.find_element(By.NAME, "personne_a_contacter").send_keys("moi")
        driver.find_element(By.NAME, "nss").send_keys("9875654321")
        driver.find_element(By.NAME, "user_email").send_keys("test@gmail.com")
        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(1)
        
        # Étape 4 : Récupérer l'ID du patient et créer le DPI
        current_url = driver.current_url
        print(f"URL actuelle après création : {current_url}")

        # Si l'ID est dans l'URL, extraire l'ID
        if "/patientT/" in current_url:
            patient_id = current_url.split("/")[5]  # L'ID est avant le dernier '/'
            print(f"ID du patient récupéré depuis l'URL : {patient_id}")
        else:
            print("L'ID n'est pas dans l'URL")
            return  # Sortir du test si l'ID n'est pas trouvé dans l'URL
        
        driver.get(f"{BASE_URL}/dpi/create-dpi/")
        driver.find_element(By.NAME, "patient_id").send_keys(patient_id)
        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)

        # Étape 5 : Vérification des résultats
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Dossier créé avec succès" in success_message.text, "Échec de la création du DPI."
        

    finally:
        # Fermer le navigateu
        driver.quit()


if __name__ == "__main__":
    test_create_dpi()