from collections import defaultdict
import streamlit as st
import pandas as pd

def tippbare_matchpunkte_buttons(offene_spiele: pd.DataFrame) -> dict:
    """Tipp pro Spiel als Dict: {(heim, gast): "6:3"}"""
    if "tipps" not in st.session_state:
        st.session_state.tipps = {}

    for _, row in offene_spiele.iterrows():
        heim, gast = row["Heim"], row["Gast"]
        matchup = (heim, gast)

        st.markdown(f"**{heim} vs. {gast}**")
        cols = st.columns(10)
        for idx, (h, g) in enumerate([(x, 9 - x) for x in reversed(range(10))]):
            label = f"{h}:{g}"
            key = f"tipp_{heim}_{gast}_{label}"

            if cols[idx].button(label, key=key):
                st.session_state.tipps[matchup] = label

        if matchup in st.session_state.tipps:
            st.caption(f"Getippt: {st.session_state.tipps[matchup]}")

    return st.session_state.tipps

def tippbare_spiele_kompakt(offene_spiele: pd.DataFrame) -> dict:
    """Zeigt offene Spiele kompakt mit RadioButtons, gibt Tipps als Ergebnis-String zurück."""
    tipps = {}
    for i, row in offene_spiele.iterrows():
        col1, col2, col3 = st.columns([3, 4, 3])
        with col1:
            st.markdown(f"**{row['Heim']}**")
        with col2:
            auswahl = st.radio(
                label="",
                options=["-", "Heimsieg", "Unentschieden", "Auswärtssieg"],
                index=0,
                horizontal=True,
                key=f"tipp_{i}"
            )
        with col3:
            st.markdown(f"**{row['Gast']}**")

        if auswahl == "Heimsieg":
            tipps[i] = "6:3"
        elif auswahl == "Unentschieden":
            tipps[i] = "5:5"
        elif auswahl == "Auswärtssieg":
            tipps[i] = "3:6"

    return tipps

def tippbare_spiele_anzeigen(offene_spiele: pd.DataFrame) -> dict:
    """Zeigt offene Spiele in Streamlit an und sammelt Tipps."""
    getippte_ergebnisse = {}

    st.subheader("📝 Offene Spiele tippen")
    for i, row in offene_spiele.iterrows():
        st.markdown(f"**{row['Heim']} vs. {row['Gast']}**")
        tipp = st.text_input("Matchpunkte (z. B. 6:3)", key=f"tipp_{i}")
        if ":" in tipp:
            getippte_ergebnisse[i] = tipp

    return getippte_ergebnisse


def merge_tipps(spiele_df: pd.DataFrame, tipps: dict) -> pd.DataFrame:
    df = spiele_df.copy()

    for (heim, gast), tipp in tipps.items():
        mask = (
            (df["Heim"] == heim) &
            (df["Gast"] == gast) &
            (df["Matchpunkte"].isin(["", "offen"]))
        )

        df.loc[mask, "Matchpunkte"] = tipp
        df.loc[mask, "Sätze"] = "0:0"
        df.loc[mask, "Spiele"] = "0:0"
        df.loc[mask, "Spielbericht"] = "anzeigen"

    return df

def berechne_tabelle(spiele_df: pd.DataFrame) -> pd.DataFrame:
    df_gespielt = spiele_df[spiele_df["Spielbericht"] == "anzeigen"].copy()

    # Tracker
    siege = defaultdict(int)
    unentschieden = defaultdict(int)
    niederlagen = defaultdict(int)
    tab_punkte = defaultdict(int)
    matchpunkte = defaultdict(lambda: [0, 0])
    saetze = defaultdict(lambda: [0, 0])
    spiele = defaultdict(lambda: [0, 0])
    begegnungen = defaultdict(int)

    for _, row in df_gespielt.iterrows():
        heim, gast = row["Heim"], row["Gast"]
        begegnungen[heim] += 1
        begegnungen[gast] += 1

        try:
            mp_h, mp_g = map(int, row["Matchpunkte"].split(":"))
            s_h, s_g = map(int, row["Sätze"].split(":"))
            sp_h, sp_g = map(int, row["Spiele"].split(":"))

            # Sieg/Unentschieden/Niederlage
            if mp_h > mp_g:
                siege[heim] += 1
                niederlagen[gast] += 1
                tab_punkte[heim] += 2
            elif mp_h < mp_g:
                siege[gast] += 1
                niederlagen[heim] += 1
                tab_punkte[gast] += 2
            else:
                unentschieden[heim] += 1
                unentschieden[gast] += 1
                tab_punkte[heim] += 1
                tab_punkte[gast] += 1

            # Rest
            matchpunkte[heim][0] += mp_h
            matchpunkte[heim][1] += mp_g
            matchpunkte[gast][0] += mp_g
            matchpunkte[gast][1] += mp_h

            saetze[heim][0] += s_h
            saetze[heim][1] += s_g
            saetze[gast][0] += s_g
            saetze[gast][1] += s_h

            spiele[heim][0] += sp_h
            spiele[heim][1] += sp_g
            spiele[gast][0] += sp_g
            spiele[gast][1] += sp_h

        except:
            continue

    alle_teams = set(spiele_df["Heim"]).union(spiele_df["Gast"])
    df = pd.DataFrame([
        {
            "Rang": None,
            "Mannschaft": team,
            "Begegnungen": begegnungen[team],
            "S": siege[team],
            "U": unentschieden[team],
            "N": niederlagen[team],
            "Tab.Punkte": f"{tab_punkte[team]}",
            "Matchpunkte": f"{matchpunkte[team][0]}:{matchpunkte[team][1]}",
            "Sätze": f"{saetze[team][0]}:{saetze[team][1]}",
            "Spiele": f"{spiele[team][0]}:{spiele[team][1]}"
        }
        for team in alle_teams
    ])

    df["Rang"] = df["Tab.Punkte"].astype(int)
    df["Matchpunkte_int"] = df["Matchpunkte"].astype(str).str.extract(r"(\d+)").astype(float)

    df = df.sort_values(
        by=["Rang", "Matchpunkte_int"],
        ascending=[False, False]
    ).drop(columns=["Rang", "Matchpunkte_int"])

    return df