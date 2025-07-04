import streamlit as st
from crawler import crawl_spiele
from tools import (
    berechne_tabelle,
    merge_tipps,
    tippbare_matchpunkte_buttons
)

URL = "https://tvbb.liga.nu/cgi-bin/WebObjects/nuLigaTENDE.woa/wa/groupPage?championship=TVBB+Sommer+2025&group=2080340"

# Init
if "tipps" not in st.session_state:
    st.session_state.tipps = {}

# Daten laden
spiele_df = crawl_spiele(URL)
offene_spiele = spiele_df[spiele_df["Spielbericht"] == "offen"].copy()

# Tipps erfassen
tipps = tippbare_matchpunkte_buttons(offene_spiele)

# Buttons
col1, col2 = st.columns(2)
with col1:
    berechnen = st.button("📊 Neue Tabelle berechnen", key="recalc_button")
with col2:
    if st.button("🧹 Tipps zurücksetzen", key="reset_button"):
        st.session_state.tipps = {}
        st.rerun()

# Merge und Berechnung
if berechnen and tipps:
    spiele_mit_tipps = merge_tipps(spiele_df, tipps)
    tabelle = berechne_tabelle(spiele_mit_tipps)
else:
    tabelle = berechne_tabelle(spiele_df)

# Immer anzeigen
st.subheader("📊 Tabelle")
st.dataframe(tabelle)

# Tabelle anzeigen

# Gespielte Partien anzeigen
abgeschlossen = spiele_df[spiele_df["Spielbericht"] == "anzeigen"].copy()
if not abgeschlossen.empty:
    st.subheader("✅ Bereits gespielte Partien")
    st.dataframe(abgeschlossen[["Datum", "Heim", "Gast", "Matchpunkte", "Sätze", "Spiele", "Spielbericht"]])