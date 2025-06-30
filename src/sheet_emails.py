import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("SHEET_ID")
SHEET_RANGE = "A2:A"

def get_sheet_service():
    creds_b64 = os.getenv("GOOGLE_SHEET_CREDS_BASE64")
    if not creds_b64:
        raise RuntimeError("❌ GOOGLE_SHEET_CREDS_BASE64 non défini dans .env")

    creds_dict = json.loads(base64.b64decode(creds_b64).decode())
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    return build("sheets", "v4", credentials=credentials)

def get_sheet_values(sheet_range="A2:A"):
    if not SHEET_ID:
        raise RuntimeError("❌ SHEET_ID non défini dans .env")

    service = get_sheet_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=sheet_range
    ).execute()

    return [row[0] for row in result.get("values", []) if row]

def add_email(email, sheet_range=SHEET_RANGE):
    if "@" not in email:
        raise ValueError("Adresse email invalide")

    existing_emails = get_sheet_values()
    if email in existing_emails:
        return  # Ne rien faire si déjà présent

    service = get_sheet_service()
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=sheet_range,
        valueInputOption="USER_ENTERED",
        body={"values": [[email]]}
    ).execute()
