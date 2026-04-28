import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Basket U14 Silver Lazio", layout="wide")

DB_FILE = "archivio_risultati.csv"

def carica_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Data", "Gara", "Risultato", "Note"])

def salva_db(nuova_riga):
    df = carica_db()
    df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

st.title("🏀 Gestione U14 Silver - Girone 3")

menu = st.sidebar.selectbox("Scegli operazione", ["Tabellone Gare", "Importa da FIP (Veloce)", "Inserimento Manuale"])

if menu == "Tabellone Gare":
    st.subheader("Archivio Risultati")
    df = carica_db()
    if df.empty:
        st.info("Nessun dato salvato. Usa le altre sezioni per aggiungere partite.")
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "Importa da FIP (Veloce)":
    st.subheader("Importazione intelligente")
    st.write("1. Vai sulla pagina FIP del Girone 3.")
    st.write("2. Seleziona tutto il testo della tabella risultati col mouse e copialo.")
    st.write("3. Incollalo qui sotto e premi 'Elabora'.")
    
    testo_incollato = st.text_area("Incolla qui il testo della pagina FIP", height=200)
    
    if st.button("Elabora e Salva"):
        # Logica per trovare le righe che sembrano una partita (Squadra A Squadra B 70-60)
        righe = testo_incollato.split('\n')
        trovati = 0
        for r in righe:
            # Cerca pattern tipo: Nome Squadra - Altra Squadra punteggio-punteggio
            match = re.search(r'(.+?)\s+-\s+(.+?)\s+(\d+)\s*-\s*(\d+)', r)
            if match:
                nuova_gara = {
                    "Data": "Importato",
                    "Gara": f"{match.group(1).strip()} - {match.group(2).strip()}",
                    "Risultato": f"{match.group(3)} - {match.group(4)}",
                    "Note": "Auto-FIP"
                }
                salva_db(nuova_gara)
                trovati += 1
        
        if trovati > 0:
            st.success(f"Ho trovato e salvato {trovati} partite!")
        else:
            st.error("Non ho trovato partite valide nel testo incollato. Assicurati di aver copiato bene la tabella.")

elif menu == "Inserimento Manuale":
    st.subheader("Inserisci Partita Singola")
    with st.form("manual"):
        g = st.text_input("Gara (es. SS Lazio - Tiber)")
        r = st.text_input("Risultato (es. 55 - 40)")
        if st.form_submit_button("Salva"):
            salva_db({"Data": "Manuale", "Gara": g, "Risultato": r, "Note": "Manuale"})
            st.success("Salvato!")
