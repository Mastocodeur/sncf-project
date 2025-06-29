import json
import os

EMAILS_PATH = os.path.join(os.path.dirname(__file__), "..", "emails.json")

def load_emails():
    if not os.path.exists(EMAILS_PATH):
        return []
    with open(EMAILS_PATH, "r") as f:
        return json.load(f)

def save_emails(emails):
    with open(EMAILS_PATH, "w") as f:
        json.dump(emails, f, indent=2)

def add_email(email):
    emails = load_emails()
    if email not in emails:
        emails.append(email)
        save_emails(emails)
