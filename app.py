import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Basket U14 - Fonte Basketincontro", layout="wide")

DB_FILE = "archivio_basketincontro.csv"

def carica_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Squadre", "Risultato", "Tabellino", "Fonte"])

def salva_db(nuovi_dati):
    df = carica_db()
    df = pd.concat([df, pd.DataFrame(nuovi_dati)], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

st.title("🏀 Gestione U14 Silver Lazio (Fonte: Basketincontro)")

scelta = st.sidebar.selectbox("Cosa vuoi fare?", ["Classifica e Risultati", "Importa Tabellini Basketincontro", "Inserimento Rapido"])

if scelta == "Classifica e Risultati":
    df = carica_db()
    if df.empty:
        st.info("Nessuna partita in archivio.")
    else:
        st.dataframe(df, use_container_width=True)

elif scelta == "Importa Tabellini Basketincontro":
    st.subheader("Cattura Risultati e Punti")
    st.markdown("""
    1. Apri la pagina del match su [Basketincontro](https://www.basketincontro.it/).
    2. Copia il testo dove vedi il punteggio e l'elenco dei giocatori con i punti.
    3. Incollalo qui sotto.
    """)
    
    testo_raw = st.text_area("Incolla qui i dati della partita", height=200)
    
    if st.button("Analizza e Salva"):
        # Cerca squadre e punteggio finale (es. SS Lazio - Tiber 70-65)
        info_gara = re.search(r'(.+?)\s+[-vV][sS]\s+(.+?)\s+(\d+)\s*[-]\s*(\d+)', testo_raw)
        
        if info_gara:
            squadre = f"{info_gara.group(1).strip()} vs {info_gara.group(2).strip()}"
            risultato = f"{info_gara.group(3)} - {info_gara.group(4)}"
            # Il resto del testo lo salviamo come tabellino
            tabellino = testo_raw.replace(info_gara.group(0), "").strip()
            
            salva_db([{"Squadre": squadre, "Risultato": risultato, "Tabellino": tabellino, "Fonte": "Basketincontro"}])
            st.success("Partita e tabellino salvati!")
        else:
            st.error("Non ho trovato squadre o punteggio nel testo. Riprova a copiare meglio.")

elif scelta == "Inserimento Rapido":
    with st.form("quick_add"):
        squadre = st.text_input("Gara")
        ris = st.text_input("Risultato finale")
        tab = st.text_area("Punti giocatori")
        if st.form_submit_button("Salva"):
            salva_db([{"Squadre": squadre, "Risultato": ris, "Tabellino": tab, "Fonte": "Manuale"}])
            st.success("Salvato!")
