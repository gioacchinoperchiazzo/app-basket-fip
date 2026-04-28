import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Basket Manager U14", layout="wide")

DB_FILE = "risultati_finali.csv"

def salva_dati(nuovi_dati):
    if os.path.exists(DB_FILE):
        df_old = pd.read_csv(DB_FILE)
        df = pd.concat([df_old, pd.DataFrame(nuovi_dati)])
    else:
        df = pd.DataFrame(nuovi_dati)
    df.drop_duplicates(subset=["Gara"], keep='last').to_csv(DB_FILE, index=False)

st.title("🏀 Risultati U14 Silver Lazio")

menu = st.sidebar.radio("Menu", ["Visualizza Archivio", "Importa Giornata (METODO SICURO)"])

if menu == "Visualizza Archivio":
    if os.path.exists(DB_FILE):
        st.table(pd.read_csv(DB_FILE))
    else:
        st.info("Archivio vuoto. Vai su 'Importa Giornata'.")

elif menu == "Importa Giornata (METODO SICURO)":
    st.subheader("Importazione Facile")
    st.write("Dato che il sito blocca l'accesso automatico, facciamo così (ci metti 5 secondi):")
    st.write("1. Vai sulla pagina di Basketincontro.")
    st.write("2. Seleziona col mouse TUTTA la tabella dei risultati.")
    st.write("3. Trascina, copia e incolla qui sotto.")
    
    giornata = st.text_input("Numero Giornata", "1")
    testo = st.text_area("Incolla qui il testo copiato dal sito", height=250)
    
    if st.button("Elabora e Salva"):
        # Questa formula magica (Regex) estrae squadre e punteggi da qualsiasi testo disordinato
        # Cerca: Nome Squadra A Nome Squadra B PuntiA - PuntiB
        pattern = r"(.+?)\s{2,}(.+?)\s+(\d+)\s*-\s*(\d+)"
        matches = re.findall(pattern, testo)
        
        if matches:
            risultati = []
            for m in matches:
                risultati.append({
                    "Giornata": giornata,
                    "Gara": f"{m[0].strip()} vs {m[1].strip()}",
                    "Punteggio": f"{m[2]} - {m[3]}"
                })
            salva_dati(risultati)
            st.success(f"Fatto! Ho ripulito il testo e salvato {len(risultati)} partite.")
        else:
            st.error("Non riesco a leggere i dati. Assicurati di aver copiato le righe con i punteggi (es: 65 - 40).")
