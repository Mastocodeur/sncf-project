import os
import pickle
import base64
import tempfile
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email_list import load_emails
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    """
    Authentifie Gmail en décodant credentials et token depuis des variables d'environnement base64.
    """
    credentials_b64 = os.getenv("CREDENTIALS_BASE64")
    token_b64 = os.getenv("TOKEN_BASE64")

    if not credentials_b64 or not token_b64:
        raise RuntimeError("❌ CREDENTIALS_BASE64 ou TOKEN_BASE64 manquant dans le fichier .env")

    with tempfile.NamedTemporaryFile(delete=False) as cred_file:
        cred_file.write(base64.b64decode(credentials_b64))
        cred_path = cred_file.name

    with tempfile.NamedTemporaryFile(delete=False) as token_file:
        token_file.write(base64.b64decode(token_b64))
        token_path = token_file.name

    with open(token_path, "rb") as f:
        creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)

def send_gmail(subject, body, to_email=None):
    """
    Envoie un e-mail via Gmail API.
    Si to_email est None, envoie à tous les abonnés de email_list.json
    """
    service = gmail_authenticate()
    recipients = [to_email] if to_email else load_emails()

    for email in recipients:
        message = MIMEText(body)
        message['to'] = email
        message['subject'] = subject
        encoded = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        service.users().messages().send(userId="me", body=encoded).execute()
