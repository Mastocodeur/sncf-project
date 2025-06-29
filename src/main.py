import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sncf import get_trains
from gmail import send_gmail
from stations import stations
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from email_list import add_email, load_emails

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

st.set_page_config(page_title="Suivi TER Nice ⇄ Monaco", layout="wide")
st_autorefresh(interval=600000, key="auto_refresh")

st.title("🚆 Suivi TER Nice Riquier ⇄ Monaco Monte Carlo")

# Formulaire d'inscription e-mail
st.subheader("✉️ S'inscrire pour recevoir les alertes retard")
with st.form("email_form"):
    new_email = st.text_input("Adresse e-mail", placeholder="exemple@gmail.com")
    submitted = st.form_submit_button("S'inscrire")
    if submitted:
        if "@" in new_email:
            add_email(new_email)
            st.success("📨 Inscription réussie ! Vous recevrez les prochaines alertes.")
        else:
            st.warning("Adresse invalide.")

# Carte
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

        def display_journeys(journeys, label):
            for journey in journeys:
                dep = datetime.strptime(journey["departure_date_time"], "%Y%m%dT%H%M%S")
                arr = datetime.strptime(journey["arrival_date_time"], "%Y%m%dT%H%M%S")
                duration = (arr - dep).seconds // 60

                delay = journey.get("durations", {}).get("departure_delay", 0)
                disruption_msg = journey.get("disruptions", [{}])[0].get("description", "")

                if delay:
                    delay_info = f"<span style='color:orange;'>⚠️ Retard : {delay // 60} min</span><br>"
                    if disruption_msg:
                        delay_info += f"<span style='color:lightgray;'>ℹ️ {disruption_msg}</span>"

                    send_gmail(
                        subject=f"🚨 Retard détecté sur le trajet : {label}",
                        body=f"""
Trajet concerné : {label}
🕒 Départ : {dep.strftime('%H:%M')}
🕒 Arrivée : {arr.strftime('%H:%M')}
⏱️ Durée : {duration} min
⚠️ Retard détecté : {delay // 60} min
ℹ️ Raison : {disruption_msg or 'Non précisée'}
                        """
                    )
                else:
                    delay_info = "<span style='color:lightgreen;'>🟢 À l'heure</span>"

                style = f"""
                <div style="background-color: #111; color: white; padding: 12px; margin-bottom: 10px;
                            border-radius: 10px; font-family: 'Courier New', monospace;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                    <strong>🕒 {dep.strftime('%H:%M')} → {arr.strftime('%H:%M')}</strong><br>
                    ⏱️ {duration} min<br>
                    {delay_info}
                </div>
                """
                st.markdown(style, unsafe_allow_html=True)

        with col1:
            st.subheader("⬅️ Nice Riquier → Monaco")
            display_journeys(nice_to_monaco, "Nice → Monaco")

        with col2:
            st.subheader("➡️ Monaco → Nice Riquier")
            display_journeys(monaco_to_nice, "Monaco → Nice")
