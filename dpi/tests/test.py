from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

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
        driver.find_element(By.NAME, "email").send_keys("administratif1@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("sarah")
        driver.find_element(By.TAG_NAME, "button").click()

        # Attendre la réponse
        time.sleep(1)
        assert "Login successful" in driver.page_source

        # Étape 2 : Veriification des permissions (si l'utilisateur a le droit de creer un dossier)
        print("Verification des roles...")
        role_user="administratif"
        roles_autorisés=["medecin","administratif"]

        #verifier si le role de l'utilisateur l'autorise à creer un compte patient
        if role_user not in roles_autorisés:
            print("Rôle non autorisé. Fin du programme.")
            driver.quit()  # Fermer le navigateur proprement
            exit()  # Quitter le programme


        #Étape 3 :Créer un dossier patient
        print("Creation du dpi...")
        driver.get(f"{BASE_URL}/dpi/create-dpi/")
        driver.find_element(By.NAME, "email").send_keys("SarahTest@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("sarah")
        

        driver.find_element(By.NAME, "nom").send_keys("Ait Kaci Azzou")
        driver.find_element(By.NAME, "prenom").send_keys("Sarah")
        driver.find_element(By.NAME, "date_naissance").send_keys("2004-10-03")
        driver.find_element(By.NAME, "adresse").send_keys("123 rue de Paris")
        driver.find_element(By.NAME, "tel").send_keys("0004556879")
        driver.find_element(By.NAME, "mutuelle").send_keys("sante")
        # Sélectionner un médecin traitant dans le menu déroulant
        select_medecin = Select(driver.find_element(By.NAME, "medecin_traitant"))
        select_medecin.select_by_value("1")  # Valeur correspondant à l'ID du médecin
        driver.find_element(By.NAME, "personne_a_contacter").send_keys("0577984641")
        driver.find_element(By.NAME, "nss").send_keys("97463415")

        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(1)
        
        

        #Étape 4 :Vérification des résultats
        success_message = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        print("DPI creer avec succes...")
        

    finally:
        # Fermer le navigateu
        driver.quit()


if __name__ == "__main__":
    test_create_dpi()