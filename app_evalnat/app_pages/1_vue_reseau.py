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

graphique_moyenne_ou_ecart(df, palette)


st.subheader("Profils et répartitions des etablissements")


plot_pie_clusters(df_feat)

  # affichage interne
# ===================================================
# 5️⃣ Lecture globale du clustering réseau
# ===================================================

with st.container(border=True):
    st.subheader("🔍 Comprendre la logique du clustering réseau")

    st.markdown("""
    Le clustering regroupe les établissements en fonction de leurs **dynamiques pédagogiques**
    sur l’ensemble des compétences du CP au CM2.

    Il repose sur une **Analyse en Composantes Principales (PCA)** permettant d’identifier
    trois axes majeurs :

    - **PC1 – Fondamentaux sémantiques :** compréhension orale/écrite, raisonnement, sens
    - **PC2 – Automatisation mathématique :** calcul mental, techniques opératoires
    - **PC3 – Complexité cognitive :** tâches intégratives, problèmes multi-étapes

    La carte PCA réseau montre comment les écoles se répartissent selon ces dimensions.
    """)

# ===================================================
# 6️⃣ Logiques pédagogiques des 4 profils
# ===================================================

with st.expander("🧬 Logique des profils (lecture réseau)"):
    st.markdown("""
    ### 🟦 Profil 1 — « Sens fort »
    Écoles centrées sur la compréhension et le raisonnement.

    ### 🟧 Profil 2 — « Intermédiaire »
    Résultats modérés, cohérence verticale fragile.

    ### 🟩 Profil 3 — « Équilibré »
    Écoles homogènes et robustes.

    ### 🟥 Profil 4 — « Procédural »
    Forte automatisation mais compréhension fragile.
    """)

# ===================================================
# 7️⃣ Diagnostic réseau
# ===================================================

with st.container(border=True):
    st.subheader("📊 Diagnostic réseau")

    # plot_pie_clusters(df_feat)

    st.markdown("""
    ### Lecture réseau
    - Le **profil dominant** révèle la culture pédagogique majoritaire du réseau.
    - Une forte part de Profil 4 → réseau orienté « automatisation ».
    - Une forte part de Profil 1 → réseau orienté « compréhension ».
    - Une forte part de Profil 2 → réseau peu structuré pédagogiquement.
    - Une forte part de Profil 3 → réseau équilibré.
    """)

# ===================================================
# 8️⃣ Recommandations réseau
# ===================================================

with st.expander("🎯 Recommandations réseau"):
    st.markdown("""
    ### Si le réseau est dominé par le Profil 4
    → Renforcer sens, lecture, vocabulaire, résolution de problèmes.

    ### Si dominé par le Profil 1
    → Déployer des rituels d’automatisation, calcul mental, techniques opératoires.

    ### Si dominé par le Profil 2
    → Structurer les progressions verticales CP–CM2 et harmoniser les pratiques.

    ### Si dominé par le Profil 3
    → Mutualiser les pratiques efficaces entre établissements.
    """)
