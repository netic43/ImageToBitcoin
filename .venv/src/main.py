import time

import base64
import hashlib
import bip39
import requests
from bitcoinlib.keys import HDKey

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size to ensure all elements are visible
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extract_text_from_span(url, class_name, driver, delay):
    # Set up Chrome options


    # Initialize ChromeDriver with options

    driver.get(url)

    try:
        # Initialize WebDriverWait with a timeout of 10 seconds
        wait = WebDriverWait(driver, delay)

        # Construct the CSS selector for the target <span> element
        css_selector = f"span.{class_name.replace(' ', '.')}"

        # Wait until the <span> element is present in the DOM
        span = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))

        # Return the text content of the <span> element
        return span.text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_bitcoin_balance(address):
    # Blockchain.com API endpoint for single address balance
    url = f'https://blockchain.info/q/addressbalance/{address}'
    time.sleep(2)

    try:
        # Send a GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # The API returns the balance in satoshis (1 BTC = 100,000,000 satoshis)
        balance_satoshis = int(response.text)
        balance_btc = balance_satoshis / 1e8  # Convert satoshis to BTC

        return balance_btc
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def image_to_address(image_path, passphrase=""):
    # Read image and convert to Base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
    base64_str = base64.b64encode(image_data).decode('utf-8')

    # Generate SHA-256 hash of Base64 data
    hash_bytes = hashlib.sha256(base64_str.encode()).digest()

    # Create mnemonic from hash
    mnemonic = bip39.encode_bytes(hash_bytes)

    # Generate seed from mnemonic and passphrase
    seed = bip39.phrase_to_seed(mnemonic, passphrase)

    # Derive BIP32 root key
    root_key = HDKey.from_seed(seed, network='bitcoin')

    # Derive path m/84'/0'/0'/0/0 for native SegWit
    child_key = root_key.subkey_for_path("m/84h/0h/0h/0/0")
    return child_key.address()


# Example usage
class_name = "sc-5f049527-7 Prcrh"
url = "https://www.blockchain.com/explorer/addresses/btc/"
img = "Images/cat.jpg"
driver = create_driver()
for i in range(37):
    address = image_to_address(f"Images/cat{i}.jpg")
    balance = extract_text_from_span(f"{url}{address}", class_name, driver, 15)
    if address == "bc1qk5hedlegkl0hrdfsw886uxc7t280sg3uhyxfdzaaq":
        print(f"\n\nFound! : cat{i}.jpg\n\n")
    print(f"Bitcoin Address: {address} \nBalance: {balance}")
driver.quit()
