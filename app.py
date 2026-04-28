import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Gestione Basket Giovanile", layout="wide")

st.title("🏀 Dashboard Risultati Basket")
st.subheader("Gestione dati FIP e inserimento manuale")

# --- DATABASE TEMPORANEO (In un caso reale useremmo un file o un database vero) ---
if 'partite' not in st.session_state:
    st.session_state.partite = pd.DataFrame(columns=[
        "Codice Gara", "Campionato", "Data", "Casa", "Ospite", "Punti Casa", "Punti Ospite", "Fonte"
    ])

# --- SIDEBAR: CARICAMENTO DATI ---
st.sidebar.header("⚙️ Operazioni")
scelta = st.sidebar.radio("Cosa vuoi fare?", ["Visualizza Risultati", "Sincronizza FIP", "Caricamento Manuale"])

if scelta == "Sincronizza FIP":
    st.info("Qui il sistema si collegherebbe a fip.it")
    url_fip = st.text_input("Incolla l'URL della pagina risultati FIP:")
    if st.button("Avvia Sincronizzazione"):
        # Simulazione di recupero dati
        nuova_gara = {
            "Codice Gara": "55001", "Campionato": "U15 Silver", "Data": "2023-11-20",
            "Casa": "Tua Squadra", "Ospite": "Avversari Basket", 
            "Punti Casa": 65, "Punti Ospite": 58, "Fonte": "FIP"
        }
        st.session_state.partite = pd.concat([st.session_state.partite, pd.DataFrame([nuova_gara])], ignore_index=True)
        st.success("Dati recuperati con successo!")

elif scelta == "Caricamento Manuale":
    st.write("### Inserisci Risultato e Tabellino")
    with st.form("form_gara"):
        col1, col2 = st.columns(2)
        with col1:
            campionato = st.selectbox("Campionato", ["Under 13", "Under 14", "Under 15", "Under 17", "Under 19", "Prima Divisione", "Promozione"])
            casa = st.text_input("Squadra Casa")
            punti_casa = st.number_input("Punti Casa", min_value=0, step=1)
        with col2:
            data = st.date_input("Data Gara")
            ospite = st.text_input("Squadra Ospite")
            punti_ospite = st.number_input("Punti Ospite", min_value=0, step=1)
        
        tabellino = st.text_area("Tabellino (es: Rossi 12, Bianchi 8, Verdi 20)")
        
        submitted = st.form_submit_button("Salva Risultato")
        if submitted:
            nuova_gara_man = {
                "Codice Gara": "MAN-" + datetime.now().strftime("%H%M%S"),
                "Campionato": campionato, "Data": str(data),
                "Casa": casa, "Ospite": ospite, 
                "Punti Casa": punti_casa, "Punti Ospite": punti_ospite, "Fonte": "Manuale"
            }
            st.session_state.partite = pd.concat([st.session_state.partite, pd.DataFrame([nuova_gara_man])], ignore_index=True)
            st.success("Risultato salvato correttamente!")

# --- PAGINA PRINCIPALE: VISUALIZZAZIONE ---
if scelta == "Visualizza Risultati":
    st.write("### Ultimi Match")
    if st.session_state.partite.empty:
        st.warning("Nessun dato presente. Vai su 'Sincronizza' o 'Manuale'.")
    else:
        st.table(st.session_state.partite)
