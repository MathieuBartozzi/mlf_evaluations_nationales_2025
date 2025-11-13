import streamlit as st
import sys, os

# Import config et fonctions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *
from fonctions_viz import *
from clustering import *


st.header("Vue d’ensemble du réseau")

df = st.session_state.get('df')
df_coordo = st.session_state.get('df_coordo')

if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez la page Home")
    st.stop()

df['Valeur'] = df['Valeur'] * 100
df["niveau_code"] = df["Niveau"].apply(lambda x: ordre_niveaux.index(x))


df_feat = construire_features(df)
df_feat, df_pca, pca, scaler, kmeans = calculer_clustering(df_feat)


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
        st.write("**Cartographie mondiale**")
        df_map = prepare_map_data(df, df_coordo)
        plot_map(df_map)  # affichage fait dans la fonction

with col2:
    with st.container(border=True):
        st.write("**Valeurs extrèmes**")
        afficher_top_bottom(df)

# =============================
# Section : Heatmap + Courbes
# =============================
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.write("**Scores par niveau et réseau**")
        heatmap_scores_par_reseau(df, ordre_niveaux)  # affichage interne

with col2:
    with st.container(border=True):

        st.write("**Évolution par matière et niveau**")
        plot_line_chart(df, palette, ordre_niveaux)  # affichage interne

# =============================
# Section : Graphique combiné
# =============================



with st.container(border=True):
    st.write("**Profils et répartitions des etablissements**")
    col1, col2 = st.columns(2)
    with col1 :
        st.markdown(
        """
        Le clustering regroupe les établissements en fonction de leurs dynamiques pédagogiques observées sur l’ensemble des compétences du **CP au CM2**. **Quatre profils** émergent de l'analyse :

        | Profil | Description synthétique |
        |--------|--------------------------|
        | **1** | Bonnes performances en compréhension et en compréhension syntaxique et textuelle, mais une automatisation encore insuffisante (calcul, techniques opératoires). |
        | **2** | Performances hétérogènes, avec une progression CP–CM2 peu régulière, suggérant une cohérence d’ensemble à renforcer. |
        | **3** | Résultats globalement équilibrés entre compréhension, automatisation et résolution complexe, avec des fragilités limitées et ciblables. |
        | **4** | Forts en procédures et raisonnement mathématique, mais des fragilités en compréhension, raisonnement et transfert dans des tâches complexes. |


        L’analyse repose sur trois axes structurants en lien avec les compétences évaluées :

        - **Axe 1 – Fondamentaux sémantiques** : compréhension orale/écrite, vocabulaire, raisonnement
        - **Axe 2 – Automatisation mathématique** : calcul mental, techniques opératoires
        - **Axe 3 – Complexité cognitive** : tâches intégratives, problèmes multi-étapes
        """
        )

    with col2:
        vue = st.segmented_control(
        "Choisissez la vue à afficher :",
        ["Répartition", "Vue 3D"],
        selection_mode="single",
        default="Répartition"
    )
        if vue =="Répartition":
            plot_pie_clusters(df_feat)
        else:
            plot_pca_3d(df_pca, ecole_selectionnee=None,palette=None)
