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
from clustering import *


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
df["niveau_code"] = df["Niveau"].apply(lambda x: ordre_niveaux.index(x))

df_feat = construire_features(df)
df_feat, df_pca, pca, scaler, kmeans = calculer_clustering(df_feat)


# ---------------------------------------------------
# 1️⃣ Sélecteur d’établissement
# ---------------------------------------------------
ecoles = sorted([str(e) for e in df["Nom_ecole"].dropna().unique()])
ecole_selectionnee = st.selectbox("Choisissez un établissement :", ecoles)

df_ecole = df[df["Nom_ecole"] == ecole_selectionnee]

# Construction clustering réseau (une seule fois)



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


with st.container(border=True):
    col1, col2 =st.columns([2,1])
    with col1 :
        plot_radar_domaine(df_ecole, df,ecole_selectionnee,palette)

    with col2 :
        plot_scatter_comparatif(df, ecole_selectionnee,palette)

# ---------------------------------------------------
# 4️⃣ Heatmap des compétences par niveau
# ---------------------------------------------------

with st.container(border=True):
    col1, col2 =st.columns([2,1])
    with col1 :
        plot_heatmap_competences(df_ecole,ordre_niveaux)
    with col2:
         plot_line_chart(df_ecole, palette, ordre_niveaux)


# --- Chargement du cluster de l'établissement ---
cluster_id = int(df_feat.loc[ecole_selectionnee, "cluster"])
profil = cluster_id + 1

with st.container(border=True):

    st.markdown(f"""
    ### 🧬 Profil {profil}
    _{description_profil(cluster_id)}_
    """)

    col1, col2 = st.columns([1, 2])

    with col1:
        plot_pie_clusters(df_feat)   # avec palette → couleurs cohérentes

    with col2:
        plot_pca_3d(df_pca, ecole_selectionnee, palette)

    with st.popover("Comprendre les 4 types de profils"):
        for pid, desc in DESCRIPTIONS_PROFILS.items():
            st.markdown(f"**Profil {pid} :** {desc}")


col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    Profil {profil}
    _{description_profil(cluster_id)}_
    """)

    plot_pca_3d(df_pca, ecole_selectionnee, palette)


with col2:
    plot_pie_clusters(df_feat)   # avec palette → couleurs cohérentes


# ===================================================
# 9️⃣ Interprétation du positionnement de l’établissement
# ===================================================

with st.container(border=True):
    st.subheader("📌 Comprendre le positionnement de l’établissement")

    pc1 = df_pca.loc[df_pca["Nom_ecole"] == ecole_selectionnee, "PC1"].values[0]
    pc2 = df_pca.loc[df_pca["Nom_ecole"] == ecole_selectionnee, "PC2"].values[0]
    pc3 = df_pca.loc[df_pca["Nom_ecole"] == ecole_selectionnee, "PC3"].values[0]

    colA, colB, colC = st.columns(3)
    colA.metric("PC1", f"{pc1:.2f}", help="Compréhension, raisonnement, lecture")
    colB.metric("PC2", f"{pc2:.2f}", help="Automatisation, calcul, techniques")
    colC.metric("PC3", f"{pc3:.2f}", help="Compétences complexes, transfert")

    st.markdown("""
    ### Lecture pédagogique
    - **PC1 élevé** → compréhension forte
    - **PC2 élevé** → automatisation forte
    - **PC3 élevé** → capacité à réussir des tâches complexes
    """)

# ===================================================
# 🔎 1️⃣0️⃣ Pourquoi cet établissement est-il dans ce profil ?
# ===================================================

with st.expander("🔎 Pourquoi cet établissement appartient à ce profil ?"):
    st.markdown(f"""
    L'établissement **{ecole_selectionnee}** appartient au **Profil {profil}**, car sa position
    dans l’espace PCA correspond à la logique pédagogique dominante de ce groupe :

    {description_profil(cluster_id)}
    """)

# ===================================================
# 1️⃣1️⃣ Recommandations pédagogiques ciblées
# ===================================================

with st.expander("🎯 Recommandations pédagogiques pour l'établissement"):

    if profil == 1:
        st.markdown("""
        ### 🟦 Profil 1 — Compréhension forte
        - Renforcer l’automatisation quotidienne
        - Développer les tâches complexes
        """)

    elif profil == 2:
        st.markdown("""
        ### 🟧 Profil 2 — Cohérence faible
        - Structurer la progression verticale
        - Installer des routines quotidiennes
        """)

    elif profil == 3:
        st.markdown("""
        ### 🟩 Profil 3 — Équilibré
        - Cibler les compétences faibles identifiées
        - Harmoniser les pratiques pédagogiques
        """)

    else:
        st.markdown("""
        ### 🟥 Profil 4 — Procédural
        - Renforcer compréhension, vocabulaire, inférences
        - Intégrer la verbalisation dans toutes les séances
        - Introduire des tâches complexes graduées
        """)

# ===================================================
# 1️⃣2️⃣ Conclusion locale
# ===================================================

with st.container(border=True):
    st.success(f"""
    ### Synthèse pour {ecole_selectionnee}

    Les données de l’établissement montrent un positionnement cohérent avec le
    **Profil {profil}**.
    La combinaison du radar, de la heatmap et de la position PCA permet de comprendre
    les forces, fragilités et dynamiques pédagogiques.
    Ces éléments servent de base au **pilotage pédagogique local**.
    """)
