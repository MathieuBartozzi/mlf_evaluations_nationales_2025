import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os

# === Import des configs et fonctions utilitaires ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *
from fonctions_viz import *

# ===================================================
# PAGE : Vue par établissement
# ===================================================
st.header("Profil d’un établissement")

# Récupération des données en session
df = st.session_state.get("df")
df_coordo = st.session_state.get("df_coordo")

if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez d’abord la page Home.")
    st.stop()

df["Valeur"] = df["Valeur"] * 100

# ---------------------------------------------------
# 1️⃣ Sélecteur d’établissement
# ---------------------------------------------------
ecoles = sorted([str(e) for e in df["Nom_ecole"].dropna().unique()])
ecole_selectionnee = st.selectbox("Choisissez un établissement :", ecoles)

df_ecole = df[df["Nom_ecole"] == ecole_selectionnee]

st.markdown(f"### 🏫 {ecole_selectionnee}")

# ---------------------------------------------------
# 2️⃣ Carte d’identité de l’établissement
# ---------------------------------------------------
# st.subheader("Carte d’identité")

# # Récupération des infos administratives
info_ecole = df_ecole[["Réseau", "Statut", "Homologué"]].drop_duplicates().iloc[0]

# col1, col2, col3 = st.columns(3)
# col1.metric("Moyenne générale", f"{df_ecole['Valeur'].mean():.1f}%", border=True)
# col2.metric("Français", f"{df_ecole[df_ecole['Matière']=='Français']['Valeur'].mean():.1f}%",border=True)
# col3.metric("Mathématiques", f"{df_ecole[df_ecole['Matière']=='Mathématiques']['Valeur'].mean():.1f}%",border=True)

# --- Calculs ---
moy_gen, delta_gen = get_moyenne_et_delta(df, df_ecole)
moy_fr, delta_fr = get_moyenne_et_delta(df, df_ecole, "Français")
moy_math, delta_math = get_moyenne_et_delta(df, df_ecole, "Mathématiques")

# --- Affichage Streamlit ---
col1, col2, col3 = st.columns(3)

col1.metric(
    "Moyenne générale",
    f"{moy_gen:.1f} %",
    delta=f"{delta_gen:+.1f} pts",
    border=True
)
col2.metric(
    "Français",
    f"{moy_fr:.1f} %",
    delta=f"{delta_fr:+.1f} pts",
    border=True
)
col3.metric(
    "Mathématiques",
    f"{moy_math:.1f} %",
    delta=f"{delta_math:+.1f} pts",
    border=True
)

# Tableau des infos
# st.table(pd.DataFrame({
#     "Réseau": [info_ecole["Réseau"]],
#     "Statut": [info_ecole["Statut"]],
#     "Homologué": [info_ecole["Homologué"]],
#     "Nombre de niveaux": [df_ecole["Niveau"].nunique()]
# }))

# ---------------------------------------------------
# 3️⃣ Radar des moyennes par domaine
# ---------------------------------------------------
# st.subheader("Forces et faiblesses par domaine")

col1, col2 =st.columns(2)
with col1 :
    plot_radar_domaine(df_ecole, df,ecole_selectionnee,palette)

with col2 :
    st.write("blabla")

# ---------------------------------------------------
# 4️⃣ Heatmap des compétences par niveau
# ---------------------------------------------------
st.subheader("Analyse des compétences par niveau")


plot_heatmap_competences(df_ecole,ordre_niveaux)
# ---------------------------------------------------
# 5️⃣ Scatterplot Math / Français (comparatif réseau)
# ---------------------------------------------------
st.subheader("Positionnement de l’établissement dans le réseau")

plot_scatter_comparatif(df, ecole_selectionnee)

# ---------------------------------------------------
# 6️⃣ Classement général
# ---------------------------------------------------
# st.subheader("Classement des établissements")

# plot_bar_classement(df, ecole_selectionnee)


