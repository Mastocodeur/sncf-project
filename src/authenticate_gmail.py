import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')

flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)

# Ne pas ouvrir automatiquement le navigateur (car ça bug en ligne de commande)
creds = flow.run_local_server(port=8083, open_browser=False)

# Enregistrement des credentials
with open(TOKEN_PATH, 'wb') as token:
    pickle.dump(creds, token)

print("✅ Authentification réussie. `token.pickle` généré.")
