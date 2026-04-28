import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Basket U14 - Gestione Stagione", layout="wide")

DB_FILE = "archivio_stagionale.csv"

def carica_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Giornata", "Gara", "Risultato"])

def salva_db(nuovo_df):
    df_attuale = carica_db()
    # Evitiamo duplicati: se la gara esiste già, non la aggiungiamo
    df_nuovo = pd.concat([df_attuale, nuovo_df]).drop_duplicates(subset=["Gara"], keep='last')
    df_nuovo.to_csv(DB_FILE, index=False)

st.title("🏀 Gestione Risultati Under 14 Silver")

menu = st.sidebar.selectbox("Menu", ["Classifica e Gare", "Carica Risultati FIP", "Inserimento Manuale"])

if menu == "Classifica e Gare":
    st.subheader("Tutti i risultati salvati")
    df = carica_db()
    if df.empty:
        st.info("Nessun dato. Vai su 'Carica Risultati FIP' per iniziare.")
    else:
        # Filtro per giornata
        giornata_scelta = st.selectbox("Filtra per giornata", ["Tutte"] + sorted(df["Giornata"].unique().tolist()))
        if giornata_scelta == "Tutte":
            st.table(df)
        else:
            st.table(df[df["Giornata"] == giornata_scelta])

elif menu == "Carica Risultati FIP":
    st.subheader("📥 Importa dati da FIP.it")
    giornata = st.selectbox("A quale giornata si riferiscono i dati?", [f"Giornata {i}" for i in range(1, 31)])
    
    st.markdown(f"""
    1. Vai sul sito FIP alla pagina del Girone 3.
    2. Seleziona la **{giornata}** dal menu a tendina sul sito FIP.
    3. Copia col mouse tutte le partite della giornata.
    4. Incolla qui sotto:
    """)
    
    testo = st.text_area("Incolla qui il testo della giornata", height=150)
    
    if st.button("Elabora e Salva Giornata"):
        # Logica migliorata per estrarre squadre e punteggi
        partite_trovate = []
        righe = testo.split('\n')
        for r in righe:
            # Cerca: Squadra A - Squadra B  60 - 45
            m = re.search(r'(.+?)\s+-\s+(.+?)\s+(\d+)\s*-\s*(\d+)', r)
            if m:
                partite_trovate.append({
                    "Giornata": giornata,
                    "Gara": f"{m.group(1).strip()} vs {m.group(2).strip()}",
                    "Risultato": f"{m.group(3)} - {m.group(4)}"
                })
        
        if partite_trovate:
            salva_db(pd.DataFrame(partite_trovate))
            st.success(f"Salvate {len(partite_trovate)} partite della {giornata}!")
        else:
            st.error("Non ho trovato risultati nel testo. Controlla di aver copiato anche il punteggio.")

elif menu == "Inserimento Manuale":
    st.subheader("✍️ Inserimento manuale singolo")
    with st.form("manual"):
        giorn = st.text_input("Giornata (es: Giornata 1)")
        g = st.text_input("Gara (es: SS Lazio - Ostia)")
        r = st.text_input("Risultato (es: 60 - 55)")
        if st.form_submit_button("Salva"):
            salva_db(pd.DataFrame([{"Giornata": giorn, "Gara": g, "Risultato": r}]))
            st.success("Salvato!")
