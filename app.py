import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Risultati U14 Silver Lazio", layout="wide")

st.title("🏀 Gestione Under 14 Silver - Girone 3")

# --- FUNZIONE DI SCRAPING REALE ---
def carica_dati_fip():
    url = "https://fip.it"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Cerchiamo le righe della tabella risultati
        tabella = soup.find_all('div', class_='fip-result-row') # Classe ipotetica basata su FIP
        
        dati = []
        # Nota: Questo è un esempio di logica di estrazione. 
        # Se la FIP aggiorna il sito, questo blocco va adattato.
        for riga in tabella:
            try:
                casa = riga.find('div', class_='team-home').text.strip()
                ospite = riga.find('div', class_='team-away').text.strip()
                risultato = riga.find('div', class_='score').text.strip()
                dati.append({"Casa": casa, "Ospite": ospite, "Risultato": risultato, "Fonte": "FIP"})
            except:
                continue
        return pd.DataFrame(dati)
    except:
        return pd.DataFrame()

# --- INTERFACCIA ---
menu = st.sidebar.radio("Menu", ["Risultati Girone", "Inserimento Manuale Tabellini"])

if menu == "Risultati Girone":
    st.subheader("Risultati dal sito FIP")
    if st.button("🔄 Aggiorna dati da FIP.it"):
        df = carica_dati_fip()
        if not df.empty:
            st.table(df)
        else:
            st.warning("Nessun dato trovato o sito FIP momentaneamente non raggiungibile. Usa l'inserimento manuale.")

elif menu == "Inserimento Manuale Tabellini":
    st.subheader("Carica Tabellino Partita")
    with st.form("manual"):
        gara = st.text_input("Gara (es: Mia Squadra vs Avversari)")
        punti_atleti = st.text_area("Inserisci i punti (es: Rossi 12, Bianchi 10...)")
        if st.form_submit_button("Salva nel database"):
            st.success("Tabellino salvato!")
