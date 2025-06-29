import os
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email_list import load_emails

TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build('gmail', 'v1', credentials=creds)
    else:
        raise RuntimeError("❌ Le token Gmail n'est pas encore généré. Lance `src/authenticate_gmail.py` d'abord.")

def send_gmail(subject, body, to_email=None):
    service = gmail_authenticate()
    emails = [to_email] if to_email else load_emails()

    for email in emails:
        message = MIMEText(body)
        message["to"] = email
        message["subject"] = subject
        encoded = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        service.users().messages().send(userId="me", body=encoded).execute()