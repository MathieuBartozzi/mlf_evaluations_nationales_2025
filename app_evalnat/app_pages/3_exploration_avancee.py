# import numpy as np
# import pandas as pd
# from scipy.stats import spearmanr
# import plotly.express as px
# import plotly.graph_objects as go
# import sys, os
# from scipy.stats import linregress, spearmanr

# # === Import des configs et fonctions utilitaires ===
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from config import *
# from fonctions_viz import *
# from clustering import *



# # ==========================================================
# # 1. CHARGEMENT DES DONNÉES DE SESSION
# # ==========================================================

# df = st.session_state.get("df")
# df_coordo = st.session_state.get("df_coordo")

# if df is None or df.empty:
#     st.warning("Aucune donnée disponible. Ouvrez d’abord la page Home.")
#     st.stop()

# df["Valeur"] = df["Valeur"] * 100

# ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]

# # ==========================================================
# # 3. INDICATEURS RÉSEAU
# # ==========================================================

# st.header("📊 Analyse réseau & Profilage des établissements")

# st.markdown("""
# ## 🧠 Comprendre les indicateurs

# - **Pente (slope)** : progression globale (positive = progresse, négative = baisse)
# - **Spearman** : régularité de la progression (1 = régulier, 0 = irrégulier)
# - **Idéal** : **pente positive + Spearman élevé**
# """)

# df_reseau = (
#     df.groupby(["Matière", "Domaine", "Compétence", "Niveau"])
#       ["Valeur"].mean()
#       .reset_index()
# )
# df_reseau["niveau_code"] = df_reseau["Niveau"].apply(lambda x: ordre_niveaux.index(x))

# # Calcul des indicateurs
# df_evol_reseau = (
#     df_reseau.groupby(["Matière", "Domaine", "Compétence"])
#       .apply(lambda g: pd.Series({
#           "slope": evolution_slope(g),
#           "spearman": evolution_spearman(g),
#           "delta": delta_first_last(g),
#           "nb_niveaux": g["niveau_code"].nunique()
#       }))
#       .reset_index()
# )

# df_plot = df_evol_reseau[df_evol_reseau["nb_niveaux"] >= 2]


# # ==========================================================
# # 4. GRAPHIQUES GLOBAUX RÉSEAU
# # ==========================================================

# st.subheader("Distribution des pentes")
# fig1 = px.histogram(df_plot, x="slope", color="Matière", nbins=25)
# st.plotly_chart(fig1, use_container_width=True)

# st.write("➡ À droite : progression forte — À gauche : régression.")

# st.subheader("Progression vs régularité")
# fig2 = px.scatter(
#     df_plot,
#     x="slope", y="spearman",
#     color="Matière",
#     hover_data=["Compétence", "Domaine"]
# )
# fig2.add_hline(y=0, line_dash="dot")
# fig2.add_vline(x=0, line_dash="dot")
# st.plotly_chart(fig2, use_container_width=True)

# # Classements
# st.header("🏆 Classements des compétences")

# col1, col2 = st.columns(2)
# with col1:
#     st.subheader("Top progressions")
#     st.dataframe(df_plot.sort_values("slope", ascending=False).head(10))

# with col2:
#     st.subheader("Top régressions")
#     st.dataframe(df_plot.sort_values("slope", ascending=True).head(10))

# st.subheader("Compétences les plus irrégulières")
# st.dataframe(df_plot[df_plot["spearman"] < 0.3].sort_values("spearman").head(10))


# # ==========================================================
# # 5. EXPLORATION D’UNE COMPÉTENCE
# # ==========================================================

# st.header("🔍 Explorer une compétence en détail")

# comp_choice = st.selectbox("Sélectionnez une compétence", df["Compétence"].unique())

# df_comp = df_reseau[df_reseau["Compétence"] == comp_choice].sort_values("niveau_code")

# fig3 = px.line(
#     df_comp,
#     x="Niveau", y="Valeur",
#     markers=True,
#     color="Niveau",
#     title=f"Évolution de : {comp_choice}"
# )
# st.plotly_chart(fig3, use_container_width=True)

# Nouveau code complet pour 3_exploration_avancee.py
# (Version avec : Stat globales, Discriminantes, Évolution, Corrélations Améliorées)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import spearmanr, pearsonr
from fonctions_viz import *

# =====================================================
# 0. Chargement des données
# =====================================================
df = st.session_state.get("df")
df_coordo = st.session_state.get("df_coordo")

if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez d’abord la page Home.")
    st.stop()

df["Valeur"] = df["Valeur"] * 100
ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]

# =====================================================
# Fonctions évolution
# =====================================================

def evolution_slope(g):
    g = g.sort_values("niveau_code")
    x = g["niveau_code"].values
    y = g["Valeur"].values
    if len(x) < 2:
        return np.nan
    return np.polyfit(x, y, 1)[0]

def evolution_spearman(g):
    g = g.sort_values("niveau_code")
    x = g["niveau_code"].values
    y = g["Valeur"].values
    return np.nan if len(x) < 2 else spearmanr(x, y)[0]

def delta_first_last(g):
    g = g.sort_values("niveau_code")
    return np.nan if g.shape[0] < 2 else g["Valeur"].iloc[-1] - g["Valeur"].iloc[0]

# =====================================================
# Préparation données réseau
# =====================================================
df_reseau = df.groupby(["Matière", "Domaine", "Compétence", "Niveau"])["Valeur"].mean().reset_index()
df_reseau["niveau_code"] = df_reseau["Niveau"].apply(lambda x: ordre_niveaux.index(x))

# =====================================================
# Calcul évolution des compétences
# =====================================================
df_evol = (
    df_reseau.groupby(["Matière", "Domaine", "Compétence"])
    .apply(lambda g: pd.Series({
        "slope": evolution_slope(g),
        "spearman": evolution_spearman(g),
        "delta": delta_first_last(g),
        "nb_niveaux": g["niveau_code"].nunique()
    }))
    .reset_index()
)
df_evol_plot = df_evol[df_evol["nb_niveaux"] >= 2]

# =====================================================
# Interface Principale
# =====================================================
st.title("🔎 Exploration avancée des compétences")

onglets = st.tabs([
    "Statistiques globales",
    "Compétences discriminantes",
    "Évolution CP → CM2",
    "Corrélations améliorées"
])

# =====================================================
# ONGLET 1 : Statistiques globales
# =====================================================
with onglets[0]:

    with st.container(border=True):
        st.subheader("Statistiques globales des compétences")


        col1, col2, col3 = st.columns(3)

        # COLONNE 1 : distribution FR/MATH
        with col1:
            # fig = px.histogram(df, x="Valeur", color="Matière", barmode="overlay", nbins=30)
            # st.plotly_chart(fig, use_container_width=True)
            plot_distribution_competences(df, nbins=10)

        # COLONNE 2 : distribution par matière sélectionnée
        with col2:
            vue_top_bottom_matiere(df, "Français", n=7)

        with col3:
            vue_top_bottom_matiere(df, "Mathématiques", n=7)


# =====================================================
# ONGLET 2 : Compétences discriminantes
# =====================================================
with onglets[1]:

    with st.container(border=True) :
        st.subheader("Compétences discriminantes ")

        st.markdown("""
                    > Une compétence est dite « discriminante » lorsqu’elle permet de distinguer clairement les établissements : les écarts de performance y sont importants. Ici, la discrimination est estimée via la dispersion des scores (écart-type). Plus l’écart-type est élevé, plus la compétence différencie les établissements : en dessous de 8 la dispersion est faible, entre 8 et 12 elle devient notable, au-delà de 12 la compétence est fortement discriminante.
                    """)
        # --- SLIDER en haut ---
        col_slider_left, col_slider_empty = st.columns([1, 3])
        with col_slider_left:
            seuil_std = st.slider(
                "Seuil de discrimination",
                min_value=7,
                max_value=17,
                value=12,
                step=1,
            )

        col1, col2=st.columns(2)
        with col1:
            st.plotly_chart(plot_swarm_competences(df, palette, seuil_std=seuil_std), use_container_width=True)

        with col2:
            st.plotly_chart(plot_scatter_dispersion(df, palette, seuil_std=seuil_std), use_container_width=True)


        df_fr, df_math = list_competences_discriminantes(df, seuil_std=seuil_std)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(df_fr, use_container_width=True)

        with col2:
            st.dataframe(df_math, use_container_width=True)




# =====================================================
# ONGLET 3 : Évolution CP → CM2
# =====================================================
with onglets[2]:

    st.subheader("Évolution des compétences CP → CM2")

    st.markdown("""
**Pente (slope) ** : intensité de la progression
  > La pente mesure l’ampleur du changement entre les niveaux d’une compétence.
  > **Positive → progression**, **négative → régression**, **faible → stagnation**.

**Corrélation de Spearman** : régularité de la progression
  > Elle indique si la montée en compétence suit un mouvement **cohérent**.
  > **Proche de 1 → progression régulière**,
  > **proche de 0 → évolution instable (montée / descente)**.

    """)

    # TOP & BOTTOM 3
    st.subheader("Top 3 / Bottom 3 des évolutions")
    top3 = df_evol_plot.sort_values("slope", ascending=False).head(3)
    bot3 = df_evol_plot.sort_values("slope", ascending=True).head(3)
    st.write("**Top 3 Progressions**")
    st.dataframe(top3)
    st.write("**Bottom 3 Régressions**")
    st.dataframe(bot3)

    # Bar domaines
    st.subheader("Progression par domaine")
    df_dom = df_evol_plot.groupby("Domaine")["slope"].mean().reset_index()
    fig_dom = px.bar(df_dom.sort_values("slope"), x="slope", y="Domaine", orientation='h')
    st.plotly_chart(fig_dom, use_container_width=True)

    # Scatter pente/spearman
    st.subheader("Régularité vs Pente")
    fig_rs = px.scatter(df_evol_plot, x="slope", y="spearman", color="Matière", hover_data=["Compétence"])
    fig_rs.add_hline(y=0)
    fig_rs.add_vline(x=0)
    st.plotly_chart(fig_rs, use_container_width=True)

    # Courbes d'évolution
    st.subheader("Courbes d'évolution par nombre de niveaux évalués")
    nb = st.selectbox("Sélectionner le nombre de niveaux", [2,3,4,5])
    comps = df_evol[df_evol["nb_niveaux"] == nb]["Compétence"].unique()

    for c in comps:
        df_c = df_reseau[df_reseau["Compétence"] == c].sort_values("niveau_code")
        fig_c = px.line(df_c, x="Niveau", y="Valeur", markers=True, title=c)
        st.plotly_chart(fig_c, use_container_width=True)

# =====================================================
# ONGLET 4 : Corrélations améliorées
# =====================================================
with onglets[3]:

    st.header("🔗 Corrélations améliorées des compétences")

    df_corr = df.pivot_table(index="Nom_ecole", columns="Compétence", values="Valeur")
    corr_matrix = df_corr.corr()

    choice = st.radio("Type de heatmap", ["Standard", "Corrélations significatives"], horizontal=True)

    if choice == "Standard":
        fig_corr = px.imshow(corr_matrix, color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_corr, use_container_width=True)

    else:
        seuil = st.slider("Seuil de significativité", 0.0, 1.0, 0.5)
        mask = corr_matrix.abs() >= seuil
        fig_corr2 = px.imshow(corr_matrix.where(mask), color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_corr2, use_container_width=True)
