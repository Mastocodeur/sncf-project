import os
import io
import pickle
import base64
import tempfile
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email_list import load_emails
from google.auth.exceptions import RefreshError
from dotenv import load_dotenv
from sheet_emails import get_sheet_values 

load_dotenv()
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    token_b64 = os.getenv("TOKEN_BASE64")
    if not token_b64:
        raise RuntimeError("❌ TOKEN_BASE64 non défini dans .env")

    try:
        # Charger depuis la chaîne base64
        token_bytes = base64.b64decode(token_b64)
        creds = pickle.load(io.BytesIO(token_bytes))

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build("gmail", "v1", credentials=creds)

    except RefreshError as e:
        raise RuntimeError(f"❌ Erreur lors du rafraîchissement du token : {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Erreur d’authentification Gmail : {e}")

def send_gmail(subject, body, to_email=None):
    """
    Envoie un e-mail via Gmail API.
    Si to_email est None, envoie à tous les abonnés dans Google Sheets.
    """
    try:
        service = gmail_authenticate()
    except RefreshError as e:
        print("❌ Erreur Gmail RefreshToken expiré :", e)
        return

    recipients = [to_email] if to_email else get_sheet_values()

    for email in recipients:
        message = MIMEText(body)
        message["to"] = email
        message["subject"] = subject
        encoded = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        try:
            service.users().messages().send(userId="me", body=encoded).execute()
        except Exception as e:
            print(f"❌ Échec de l'envoi à {email} : {e}")