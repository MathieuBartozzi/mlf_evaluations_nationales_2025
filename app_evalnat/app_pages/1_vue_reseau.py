import streamlit as st
import sys, os

# Import config et fonctions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *
from fonctions_viz import *

st.header("Vue d’ensemble du réseau")

df = st.session_state.get('df')
df_coordo = st.session_state.get('df_coordo')

if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez la page Home")
    st.stop()

df['Valeur'] = df['Valeur'] * 100

# =============================
# Section : Indicateurs clés
# =============================
col1, col2, col3 = st.columns(3)
moy_globale = df["Valeur"].mean()
moy_maths = df.loc[df["Matière"] == "Mathématiques", "Valeur"].mean()
moy_fr = df.loc[df["Matière"] == "Français", "Valeur"].mean()

col1.metric("Moyenne générale", f"{moy_globale:.0f} %", border=True)
col2.metric("Mathématiques", f"{moy_maths:.0f}%", border=True)
col3.metric("Français", f"{moy_fr:.0f}%", border=True)

# =============================
# Section : Carte + Top/Bottom
# =============================
col1, col2 = st.columns([2, 1])
with col1:
    with st.container(border=True):
        df_map = prepare_map_data(df, df_coordo)
        plot_map(df_map)  # affichage fait dans la fonction

with col2:
    with st.container(border=True):
        afficher_top_bottom(df)

# =============================
# Section : Heatmap + Courbes
# =============================
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        heatmap_scores_par_reseau(df, ordre_niveaux)  # affichage interne

with col2:
    with st.container(border=True):
        plot_line_chart(df, palette, ordre_niveaux)  # affichage interne

# =============================
# Section : Graphique combiné
# =============================
with st.container(border=True):
    graphique_moyenne_ou_ecart(df, palette)  # affichage interne
