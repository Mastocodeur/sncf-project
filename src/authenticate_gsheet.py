import os
import json
import base64
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

def get_gsheet_client():
    # Charger la clé JSON depuis la variable d'environnement (base64)
    key_b64 = os.getenv("GOOGLE_SHEET_CREDS_BASE64")
    if not key_b64:
        raise ValueError("⛔ GDRIVE_KEY_BASE64 n'est pas défini dans .env")

    key_json = base64.b64decode(key_b64).decode("utf-8")
    credentials_info = json.loads(key_json)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(creds)
    return client

if __name__ == "__main__":
    SHEET_ID = os.getenv("SHEET_ID")
    if not SHEET_ID:
        raise ValueError("⛔ SHEET_ID manquant dans .env")

    client = get_gsheet_client()
    sheet = client.open_by_key(SHEET_ID).sheet1  # première feuille

    print("✅ Connexion réussie à Google Sheets")
    print("📋 Données actuelles :")
    for row in sheet.get_all_values():
        print(row)
