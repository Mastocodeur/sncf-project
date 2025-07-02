"""
Application Streamlit pour le suivi des trains TER entre Nice Riquier et Monaco Monte Carlo.
- Affiche les prochains départs et arrivées
- Détecte les retards et envoie une alerte par email aux utilisateurs inscrits
- Permet l'inscription via formulaire, stockée dans Google Sheets
- Récupère les données SNCF via l'API Navitia
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sncf import get_trains
from gmail import send_gmail
from stations import stations
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from sheet_emails import add_email, get_sheet_values  # Gestion des emails via Google Sheets

# Chargement des variables d'environnement
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuration de la page Streamlit
st.set_page_config(page_title="Suivi TER Nice ⇄ Monaco", layout="wide")

# Rafraîchissement automatique toutes les 10 minutes
st_autorefresh(interval=600000, key="auto_refresh")

st.title("🚆 Suivi TER Nice Riquier ⇄ Monaco Monte Carlo")

# Formulaire d'inscription e-mail
st.subheader("✉️ S'inscrire pour recevoir les alertes des retards de votre trajet ZOU")
with st.form("email_form"):
    new_email = st.text_input("Adresse e-mail", placeholder="exemple@gmail.com")
    submitted = st.form_submit_button("S'inscrire")
    if submitted:
        if "@" in new_email:
            add_email(new_email)
            st.success("📨 Inscription réussie. Vous recevrez les prochaines alertes.")
        else:
            st.warning("Adresse invalide.")

# Carte des gares
st.subheader("📍 Localisation des gares")
for name, data in stations.items():
    maps_url = f"https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}"
    st.markdown(f"- **[{name}]({maps_url})** ([{data['lat']}, {data['lon']}]) 🌍")

st.map(pd.DataFrame([{"lat": s["lat"], "lon": s["lon"]} for s in stations.values()]), zoom=11)

# Rafraîchissement
refresh_clicked = st.button("🔄 Rafraîchir maintenant")

if refresh_clicked or st.session_state.get("auto_refresh_ran", False) is False:
    with st.spinner("Chargement des horaires..."):
        st.session_state["auto_refresh_ran"] = True

        nice_to_monaco = get_trains(stations["Nice Riquier"]["id"], stations["Monaco Monte Carlo"]["id"])
        monaco_to_nice = get_trains(stations["Monaco Monte Carlo"]["id"], stations["Nice Riquier"]["id"])

        col1, col2 = st.columns(2)

        def extract_delay(journey, stop_id_prefix):
            """
            Calcule le retard en minutes à partir du stop_point correspondant à la gare de départ réelle.
            """
            section = next((s for s in journey.get("sections", []) if s.get("type") == "public_transport"), None)
            if not section:
                return 0
            for stop in section.get("stop_date_times", []):
                stop_id = stop.get("stop_point", {}).get("id", "")
                if stop_id_prefix in stop_id:
                    try:
                        base = datetime.strptime(stop["base_departure_date_time"], "%Y%m%dT%H%M%S")
                        real = datetime.strptime(stop["departure_date_time"], "%Y%m%dT%H%M%S")
                        return int((real - base).total_seconds() / 60)
                    except Exception:
                        return 0
            return 0

        def display_journeys(journeys, label, stop_id_prefix):
            """
            Affiche les horaires de trajets.
            En cas de retard, envoie une alerte aux emails récupérés depuis Google Sheets.
            """
            for journey in journeys:
                dep = datetime.strptime(journey["departure_date_time"], "%Y%m%dT%H%M%S")
                arr = datetime.strptime(journey["arrival_date_time"], "%Y%m%dT%H%M%S")
                duration = (arr - dep).seconds // 60

                delay = extract_delay(journey, stop_id_prefix)
                disruption_msg = journey.get("disruptions", [{}])[0].get("description", "")

                sections = journey.get("sections", [])
                pt_section = next((s for s in sections if s.get("type") == "public_transport"), {})
                train_info = pt_section.get("display_informations", {})
                train_number = train_info.get("headsign", "—")
                platform = pt_section.get("departure", {}).get("platform", "—")

                if delay:
                    delay_info = f"<span style='color:orange;'>⚠️ Retard : {delay} min</span><br>"
                    if disruption_msg:
                        delay_info += f"<span style='color:lightgray;'>ℹ️ {disruption_msg}</span>"

                    for email in get_sheet_values():
                        send_gmail(
                            subject=f"🚨 Retard détecté sur le trajet : {label}",
                            body=f"""
Trajet concerné : {label}
🕒 Départ : {dep.strftime('%H:%M')}
🕒 Arrivée : {arr.strftime('%H:%M')}
⏱️ Durée : {duration} min
🚆 Numéro de Train : {train_number}
🛤️ Voie : {platform}
⚠️ Retard détecté : {delay} min
ℹ️ Raison : {disruption_msg or 'Non précisée'}
                            """,
                            to_email=email
                        )
                else:
                    delay_info = "<span style='color:lightgreen;'>🟢 À l'heure</span>"

                style = f"""
                <div style="background-color: #111; color: white; padding: 12px; margin-bottom: 10px;
                            border-radius: 10px; font-family: 'Courier New', monospace;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                    <strong>🕒 {dep.strftime('%H:%M')} → {arr.strftime('%H:%M')}</strong><br>
                    🚆 Train : {train_number} | 🛤️ Voie : {platform}<br>
                    ⏱️ {duration} min<br>
                    {delay_info}
                </div>
                """
                st.markdown(style, unsafe_allow_html=True)

        with col1:
            st.subheader("⬅️ Nice Riquier → Monaco")
            display_journeys(nice_to_monaco, "Nice → Monaco", stop_id_prefix="87756353")

        with col2:
            st.subheader("➡️ Monaco → Nice Riquier")
            display_journeys(monaco_to_nice, "Monaco → Nice", stop_id_prefix="87756403")
