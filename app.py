import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Basket Manager U14", layout="wide")

# File per i dati
GERE_FILE = "gare.csv"
TABELLINI_FILE = "tabellini.csv"

def carica_dati(file, colonne):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=colonne)

def salva_dati(file, nuovo_df):
    df_attuale = pd.read_csv(file) if os.path.exists(file) else pd.DataFrame(columns=nuovo_df.columns)
    pd.concat([df_attuale, nuovo_df]).drop_duplicates().to_csv(file, index=False)

st.title("🏀 Gestore Risultati & Tabellini U14")

menu = st.sidebar.selectbox("Menu", ["🏠 Dashboard Risultati", "📅 Carica Giornata (Risultati)", "📊 Carica Tabellino (Punti Atleti)"])

# --- 1. DASHBOARD ---
if menu == "🏠 Dashboard Risultati":
    st.subheader("Risultati Campionato")
    gare = carica_dati(GERE_FILE, ["Giornata", "Partita", "Risultato"])
    if gare.empty: st.info("Nessuna gara salvata.")
    else: st.table(gare)
    
    st.subheader("Dettaglio Tabellini")
    tabs = carica_dati(TABELLINI_FILE, ["Partita", "Punti_Giocatori"])
    if tabs.empty: st.info("Nessun tabellino salvato.")
    else: st.table(tabs)

# --- 2. CARICA GIORNATA ---
elif menu == "📅 Carica Giornata (Risultati)":
    st.subheader("Importa Risultati di una Giornata")
    giornata = st.text_input("Quale giornata? (es: 1 Ritorno)")
    testo = st.text_area("Incolla qui i risultati dal sito (anche disordinati)", height=150)
    
    if st.button("Salva Risultati"):
        # Cerca pattern: Squadra A - Squadra B 70 - 60
        matches = re.findall(r'(.+?)\s+-\s+(.+?)\s+(\d+)\s*-\s*(\d+)', testo)
        if matches:
            nuove_gare = [{"Giornata": giornata, "Partita": f"{m[0].strip()} - {m[1].strip()}", "Risultato": f"{m[2]}-{m[3]}"} for m in matches]
            salva_dati(GERE_FILE, pd.DataFrame(nuove_gare))
            st.success(f"Salvate {len(nuove_gare)} partite!")
        else: st.error("Non ho trovato risultati. Prova a copiare meglio la riga della partita.")

# --- 3. CARICA TABELLINO ---
elif menu == "📊 Carica Tabellino (Punti Atleti)":
    st.subheader("Importa Tabellino Singolo")
    gare_esistenti = carica_dati(GERE_FILE, ["Partita"])["Partita"].unique()
    partita_sel = st.selectbox("Seleziona la partita", gare_esistenti if len(gare_esistenti)>0 else ["Inserisci prima i risultati"])
    testo_tab = st.text_area("Incolla qui i punti (es: Rossi 12, Bianchi 8...)")
    
    if st.button("Salva Tabellino"):
        if partita_sel != "Inserisci prima i risultati":
            salva_dati(TABELLINI_FILE, pd.DataFrame([{"Partita": partita_sel, "Punti_Giocatori": testo_tab}]))
            st.success("Tabellino collegato alla partita!")
