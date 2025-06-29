# 🚆 Suivi TER Nice ⇄ Monaco

Application Streamlit pour suivre en temps réel les trains entre **Nice Riquier** et **Monaco Monte Carlo**, avec visualisation des horaires et alertes e-mail en cas de retard.

---

## 🎯 Objectif

L’application permet de :
- Suivre les trajets TER dans les deux sens (Nice ⇄ Monaco)
- Être alerté par e-mail en cas de **retard ou perturbation**
- Visualiser les horaires de départs/arrivées dans une interface de type **tableau de gare**

---

## 🔌 Données utilisées

Les données proviennent de l’**API SNCF (Navitia)** :  
https://api.sncf.com/

Cette API permet d’accéder en temps réel aux horaires, retards, causes de perturbations, etc.

---

## 🧱 Technologies

- 🐍 Python 3.10+
- ⚡ Streamlit
- 📡 API SNCF
- 📬 Gmail API (OAuth 2.0)
- 🧪 Pandas, Requests
- 🔒 `python-dotenv` pour la gestion des secrets
- 🚀 [`uv`](https://github.com/astral-sh/uv) pour l’installation rapide des dépendances

---

## ⚡ Installation avec `uv`

1. **Cloner le dépôt** :

```bash
git clone https://github.com/Mastocodeur/sncf-project.git
cd sncf-project
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml
```

2. **Ajouter un fichier .env à la racine** :

```bash
SNCF_API_KEY=ta_cle_api_sncf
EMAIL_DEST=ton_adresse_email@example.com
```

3. Placer le fichier `credentials.json` (Gmail OAuth) à la racine

## 🔐 Configuration de l'API Gmail (OAuth 2.0)
### ✅ Étape 1 – Créer un projet Google Cloud

1. Accéder à Google Cloud Console
2. Créer un nouveau projet (ex. : sncf-project)

### ✅ Étape 2 – Activer l'API Gmail

* Menu > API & Services > Bibliothèque
* Rechercher Gmail API → Activer

### ✅ Étape 3 – Créer un identifiant OAuth 2.0

* Menu > Identifiants > Créer des identifiants > ID client OAuth
* Type d'application : Application de bureau
* Télécharger le fichier `.json` et le renommer en `credentials.json`

### ✅ Étape 4 – Ajouter les URI de redirection
Dans la configuration OAuth, ajouter les URI suivantes :

* http://localhost:8080/
* http://localhost:8083/

## ✅ Étape 5 – Générer le fichier token.pickle

Créer un fichier src/authenticate_gmail.py :

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=8083)

with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)

print("✅ Token enregistré sous token.pickle")
```

Exécuter une seule fois :

```bash
python src/authenticate_gmail.py
```

Une URL de validation s’affichera dans le terminal : ouvrir dans un navigateur, autoriser, et le token sera généré.

### ✅ Étape 6 – Ajouter l’adresse Gmail comme testeur
* Accéder à Écran de consentement OAuth
* Ajouter l’adresse Gmail utilisée dans la section Utilisateurs testeurs

## ▶️ Lancer l’application

```bash
streamlit run src/main.py
```

## 🧪 Notebooks d’exploration
`notebooks/01_exploration_api_sncf.ipynb` :
* Recherche de gares par nom
* Récupération de trajets
* Analyse des horaires, retards, perturbations
* Exploration via pandas

`notebooks/02_gmail.ipynb` : 
* Test de l’authentification Gmail
* Envoi d’e-mails via l’API

## 📬 Alerte automatique par e-mail
En cas de retard détecté, un e-mail est envoyé automatiquement grâce à l’API Gmail.

L'adresse destinataire est configurable via `EMAIL_DEST` dans le fichier `.env`.