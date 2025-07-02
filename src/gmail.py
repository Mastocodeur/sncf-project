import os
import io
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from dotenv import load_dotenv
from sheet_emails import get_sheet_values
from typing import Optional

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    token_b64 = os.getenv("TOKEN_PICKLE_B64")
    if not token_b64:
        raise RuntimeError("❌ TOKEN_PICKLE_B64 non défini dans .env")

    try:
        token_bytes = base64.b64decode(token_b64)
        creds = pickle.load(io.BytesIO(token_bytes))

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build("gmail", "v1", credentials=creds)

    except RefreshError as e:
        raise RuntimeError(f"❌ Erreur lors du rafraîchissement du token : {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Erreur d’authentification Gmail : {e}")

def send_gmail(subject: str, body: str, to_email: Optional[str] = None):
    """
    Envoie un e-mail via Gmail API.
    Si `to_email` est None, envoie à tous les abonnés Google Sheets.
    """
    try:
        service = gmail_authenticate()
    except Exception as e:
        print("❌ Erreur Gmail :", e)
        return

    recipients = [to_email] if to_email else get_sheet_values()

    for email in recipients:
        message = MIMEText(body)
        message["to"] = email
        message["subject"] = subject
        encoded = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        try:
            service.users().messages().send(userId="me", body=encoded).execute()
            print(f"📤 Envoi réussi à {email}")
        except Exception as e:
            print(f"❌ Échec de l'envoi à {email} : {e}")
