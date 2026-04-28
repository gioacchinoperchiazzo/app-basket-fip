import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Basket Manager - Basketincontro", layout="wide")

# File per salvare i dati
GARE_FILE = "gare_basketincontro.csv"
TABS_FILE = "tabellini_atleti.csv"

def carica_file(nome_file, colonne):
    if os.path.exists(nome_file):
        return pd.read_csv(nome_file)
    return pd.DataFrame(columns=colonne)

def salva_file(nome_file, nuovo_df):
    df_esistente = carica_file(nome_file, nuovo_df.columns)
    # Evitiamo duplicati basandoci sulla colonna 'Incontro'
    df_finale = pd.concat([df_esistente, nuovo_df]).drop_duplicates(subset=["Incontro"], keep='last')
    df_finale.to_csv(nome_file, index=False)

st.title("🏀 U14 Regionale - Gestione Basketincontro")

menu = st.sidebar.radio("Menu Principale", ["🏠 Tabellone Generale", "📥 Importa da Basketincontro", "📊 Inserisci Tabellino Atleti"])

# --- 1. VISUALIZZAZIONE ---
if menu == "🏠 Tabellone Generale":
    st.subheader("Risultati Salvati")
    df_gare = carica_file(GARE_FILE, ["Giornata", "Incontro", "Risultato"])
    if df_gare.empty:
        st.info("L'archivio è vuoto. Vai alla sezione Importa.")
    else:
        st.table(df_gare)

# --- 2. IMPORTAZIONE ---
elif menu == "📥 Importa da Basketincontro":
    st.subheader("Importazione Rapida Giornata")
    st.info("Apri la giornata su Basketincontro, copia la tabella dei risultati e incollala qui.")
    
    giornata_n = st.text_input("Specifica la Giornata (es: 1 Andata)", "1")
    testo_incollato = st.text_area("Incolla qui il testo dei risultati", height=200)
    
    if st.button("Elabora e Salva"):
        # Logica specifica per il formato Basketincontro: Squadra A Squadra B 60 - 45
        # Cerchiamo pattern tipo "Virtus Roma BK Frascati 55 - 40"
        partite = []
        righe = testo_incollato.split('\n')
        for r in righe:
            # Questa espressione cerca due nomi di squadre seguiti da un punteggio X - Y
            match = re.search(r'(.+?)\s+(.+?)\s+(\d+)\s*-\s*(\d+)', r)
            if match:
                partite.append({
                    "Giornata": giornata_n,
                    "Incontro": f"{match.group(1).strip()} vs {match.group(2).strip()}",
                    "Risultato": f"{match.group(3)} - {match.group(4)}"
                })
        
        if partite:
            salva_file(GARE_FILE, pd.DataFrame(partite))
            st.success(f"Ho trovato e salvato {len(partite)} partite!")
        else:
            st.error("Non ho trovato risultati validi. Assicurati che nel testo incollato ci sia il punteggio (es. 50 - 40).")

# --- 3. TABELLINI ---
elif menu == "📊 Inserisci Tabellino Atleti":
    st.subheader("Punti Individuali")
    df_gare = carica_file(GARE_FILE, ["Incontro"])
    if df_gare.empty:
        st.warning("Devi prima importare i risultati delle gare!")
    else:
        partita_sel = st.selectbox("Seleziona la partita", df_gare["Incontro"].unique())
        punti_testo = st.text_area("Incolla il tabellino (es: Rossi 15, Bianchi 4...)")
        if st.button("Salva Tabellino"):
            salva_file(TABS_FILE, pd.DataFrame([{"Incontro": partita_sel, "Punti": punti_testo}]))
            st.success("Tabellino salvato con successo!")

