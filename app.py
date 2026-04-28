import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import re

st.set_page_config(page_title="Basket Manager U14", layout="wide")

DB_FILE = "archivio_basket.csv"

def carica_db():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Giornata", "Incontro", "Risultato"])

def salva_db(nuovo_df):
    df_attuale = carica_db()
    df_finale = pd.concat([df_attuale, nuovo_df]).drop_duplicates(subset=["Incontro"], keep='last')
    df_finale.to_csv(DB_FILE, index=False)

# --- FUNZIONE DI IMPORTAZIONE AUTOMATICA ---
def importa_da_url(url, giornata_label):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, "Errore: Il sito ha negato l'accesso (Status Code: " + str(response.status_code) + ")"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        partite = []
        
        # Cerchiamo le righe dei risultati nel formato Basketincontro
        # Nota: Le classi CSS possono variare, questa è una ricerca flessibile
        rows = soup.find_all(['div', 'tr'], class_=re.compile(r'match|result|row'))
        
        for r in rows:
            testo = r.get_text(separator=" ").strip()
            # Cerca pattern: Squadra A Squadra B 70 - 65
            m = re.search(r'(.+?)\s+(.+?)\s+(\d+)\s*-\s*(\d+)', testo)
            if m:
                partite.append({
                    "Giornata": giornata_label,
                    "Incontro": f"{m.group(1).strip()} vs {m.group(2).strip()}",
                    "Risultato": f"{m.group(3)} - {m.group(4)}"
                })
        
        if not partite:
            return None, "Nessuna partita trovata. Il formato della pagina potrebbe essere cambiato."
        return pd.DataFrame(partite), None
    except Exception as e:
        return None, f"Errore tecnico: {str(e)}"

# --- INTERFACCIA ---
st.title("🏀 Gestione U14 Regionale")

menu = st.sidebar.radio("Menu", ["Visualizza Archivio", "Importa da Link", "Inserimento Manuale"])

if menu == "Visualizza Archivio":
    st.subheader("Tutti i Risultati Salvati")
    df = carica_db()
    if df.empty: st.info("Archivio vuoto.")
    else: st.dataframe(df, use_container_width=True)

elif menu == "Importa da Link":
    st.subheader("Carica Giornata via URL")
    url_input = st.text_input("Incolla il link di Basketincontro:", "https://basketincontro.it")
    giornata_n = st.text_input("Etichetta Giornata (es: 1 Andata):", "1")
    
    if st.button("🚀 Importa Automaticamente"):
        with st.spinner("Connessione a Basketincontro in corso..."):
            df_risultati, errore = importa_da_url(url_input, giornata_n)
            
            if errore:
                st.error(errore)
                st.warning("Usa il 'Copia e Incolla' nel menu Inserimento Manuale se l'automatico fallisce.")
            else:
                st.success(f"Trovate {len(df_risultati)} partite!")
                st.table(df_risultati)
                if st.button("Conferma e Salva in Archivio"):
                    salva_db(df_risultati)
                    st.balloons()

elif menu == "Inserimento Manuale":
    st.subheader("Copia e Incolla (Metodo Sicuro)")
    testo = st.text_area("Incolla qui il testo della pagina se l'importazione automatica non funziona:")
    if st.button("Elabora Testo"):
        # Logica di emergenza per estrarre dati dal testo incollato
        matches = re.findall(r'(.+?)\s+-\s+(.+?)\s+(\d+)\s*-\s*(\d+)', testo)
        if matches:
            df_man = pd.DataFrame([{"Giornata": "Manuale", "Incontro": f"{m[0]} vs {m[1]}", "Risultato": f"{m[2]}-{m[3]}"} for m in matches])
            salva_db(df_man)
            st.success("Partite salvate!")
        else: st.error("Formato non riconosciuto.")
