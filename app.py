import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

st.set_page_config(page_title="Basket U14 Silver", layout="wide")

DB_FILE = "risultati_persistenti.csv"

def carica_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Data", "Gara", "Risultato", "Fonte"])

def salva_db(nuova_riga):
    df = carica_db()
    df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- FUNZIONE TENTATIVO FIP ---
def recupera_da_fip():
    url = "https://fip.it"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerchiamo i blocchi delle partite nel nuovo formato FIP
        partite = []
        blocchi = soup.select('.fip-calendar-match-item, .match-item, .risultato-gara') 
        
        for b in blocchi:
            try:
                team_casa = b.select_one('.home-team, .team-name').text.strip()
                team_ospite = b.select_one('.away-team, .team-name-away').text.strip()
                score = b.select_one('.score, .result').text.strip()
                partite.append({"Data": "Da sito FIP", "Gara": f"{team_casa} - {team_ospite}", "Risultato": score, "Fonte": "FIP"})
            except: continue
        return pd.DataFrame(partite)
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏀 Gestione Risultati U14 Silver")

menu = st.sidebar.selectbox("Cosa vuoi fare?", ["Tabellone Generale", "Sincronizza FIP", "Carica Manuale"])

if menu == "Tabellone Generale":
    st.subheader("Risultati Salvati")
    dati = carica_db()
    if dati.empty:
        st.info("L'archivio è vuoto. Usa le altre opzioni del menu per popolarlo.")
    else:
        st.dataframe(dati, use_container_width=True)

elif menu == "Sincronizza FIP":
    st.subheader("Tentativo recupero automatico")
    st.write("Questo tasto proverà a leggere il sito fip.it per il Girone 3.")
    if st.button("Avvia Scraper"):
        risultati_fip = recupera_da_fip()
        if not risultati_fip.empty:
            st.write("Ho trovato queste partite:")
            st.table(risultati_fip)
            if st.button("Salva questi dati nell'archivio"):
                for _, row in risultati_fip.iterrows():
                    salva_db(row)
                st.success("Dati importati!")
        else:
            st.error("Non è stato possibile estrarre i dati. Il sito FIP potrebbe avere protezioni attive.")

elif menu == "Carica Manuale":
    st.subheader("Inserimento Manuale")
    with st.form("manual_form"):
        data_g = st.date_input("Data")
        gara_txt = st.text_input("Gara (es. Lazio - Ostia)")
        ris_txt = st.text_input("Risultato (es. 70 - 65)")
        if st.form_submit_button("Salva Partita"):
            salva_db({"Data": str(data_g), "Gara": gara_txt, "Risultato": ris_txt, "Fonte": "Manuale"})
            st.success("Salvato!")
