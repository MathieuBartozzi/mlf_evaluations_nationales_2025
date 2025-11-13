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


# # Récupération des données en session
# df = st.session_state.get("df")
# df_coordo = st.session_state.get("df_coordo")

# if df is None or df.empty:
#     st.warning("Aucune donnée disponible. Ouvrez d’abord la page Home.")
#     st.stop()

# df["Valeur"] = df["Valeur"] * 100




# st.subheader("Vue réseau – toutes les écoles")

# # ---------------------------------------------------------
# # Introduction pédagogique
# # ---------------------------------------------------------

# st.markdown("""
# ## 🧠 Comprendre les indicateurs

# > La **pente** mesure comment la compétence **progresse** d’un niveau à l’autre : positive (progression), négative (régression), proche de 0 (stabilité)

# > Le **coefficient de Spearman** mesure **la régularité de l'évolution** : 1.0 (progression régulière), 0.0 (évolution irrégulière), négatif (monte puis descend)

# > Une compétence idéale aurait : une **pente positive** et **un Spearman élevé**
# """)

# # ---------------------------------------------------------
# # Calcul des indicateurs réseau
# # ---------------------------------------------------------


# df_reseau = (
#     df.groupby(["Matière", "Domaine", "Compétence", "Niveau"])
#       ["Valeur"].mean()
#       .reset_index()
# )

# ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]

# df_reseau["niveau_code"] = df_reseau["Niveau"].apply(
#     lambda x: ordre_niveaux.index(x)
# )

# df["niveau_code"] = df["Niveau"].apply(
#     lambda x: ordre_niveaux.index(x)
# )


# def evolution_slope(g):
#     if g["niveau_code"].nunique() < 2:
#         return np.nan
#     slope, _, _, _, _ = linregress(g["niveau_code"], g["Valeur"])
#     return slope

# def evolution_spearman(g):
#     if g["niveau_code"].nunique() < 2:
#         return np.nan
#     corr, _ = spearmanr(g["niveau_code"], g["Valeur"])
#     return corr

# def delta_first_last(g):
#     if g["niveau_code"].nunique() < 2:
#         return np.nan
#     g = g.sort_values("niveau_code")
#     return g["Valeur"].iloc[-1] - g["Valeur"].iloc[0]

# # Agrégation réseau
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

# # ---------------------------------------------------------
# # SECTION 2 — Vue globale réseau
# # ---------------------------------------------------------

# st.subheader("Distribution des pentes (progression des compétences)")
# fig1 = px.histogram(
#     df_plot,
#     x="slope",
#     color="Matière",
#     nbins=25,
#     title="Histogramme des pentes d’évolution",
#     labels={"slope": "Pente (slope)"}
# )
# st.plotly_chart(fig1, use_container_width=True)

# st.write("""
# ➡ **Plus la barre est à droite**, plus la compétence progresse fortement.
# ➡ **Barres à gauche** : compétences qui régressent.
# """)

# # ---------------------------------------------------------
# # Scatter slope vs Spearman
# # ---------------------------------------------------------
# st.subheader("Progression vs Régularité des compétences")
# fig2 = px.scatter(
#     df_plot,
#     x="slope",
#     y="spearman",
#     color="Matière",
#     hover_data=["Compétence", "Domaine"],
#     title="Relation entre pente (progression) et Spearman (régularité)"
# )
# fig2.add_hline(y=0, line_dash="dot")
# fig2.add_vline(x=0, line_dash="dot")
# st.plotly_chart(fig2, use_container_width=True)

# st.write("""
# 🟦 Zone en haut à droite : **Compétences solides** (progression + régularité)
# 🟧 Zone en bas à droite : **Progression mais irrégulière** (à surveiller)
# 🟥 Zone en bas à gauche : **Régression + incohérence** (points critiques)
# """)

# # ---------------------------------------------------------
# # SECTION 3 — Classements
# # ---------------------------------------------------------
# st.header("🏆 Classements des compétences")

# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("Top progressions")
#     top_pos = df_plot.sort_values("slope", ascending=False).head(10)
#     st.dataframe(top_pos)

# with col2:
#     st.subheader("Top régressions")
#     top_neg = df_plot.sort_values("slope", ascending=True).head(10)
#     st.dataframe(top_neg)

# st.subheader("Compétences les plus irrégulières (Spearman faible)")
# incoh = df_plot[df_plot["spearman"] < 0.3].sort_values("spearman").head(10)
# st.dataframe(incoh)

# # ---------------------------------------------------------
# # SECTION 4 — Exploration interactive
# # ---------------------------------------------------------
# st.header("🔍 Explorer une compétence en détail")

# comp_choice = st.selectbox(
#     "Sélectionnez une compétence",
#     df["Compétence"].unique()
# )

# df_comp = df_reseau[df_reseau["Compétence"] == comp_choice].sort_values("niveau_code")
# ##['Matière', 'Domaine', 'Compétence', 'Niveau', 'Valeur', 'niveau_code']
# fig3 = px.line(
#     df_comp,
#     x="Niveau",
#     y="Valeur",
#     color="Niveau",
#     markers=True,
#     title=f"Évolution de la compétence : {comp_choice}"
# )

# st.plotly_chart(fig3, use_container_width=True)


# df_plot["selected"] = df_plot["Compétence"] == comp_choice
# df_plot["point_size"] = df_plot["selected"].apply(lambda x: 25 if x else 8)
# df_plot["point_color"] = df_plot["selected"].apply(lambda x: "red" if x else "gray")
# df_plot["label"] = df_plot["Compétence"].where(df_plot["selected"], "")

# fig = px.scatter(
#     df_plot,
#     x="slope",
#     y="spearman",
#     text="label",
#     color="point_color",
#     size="point_size",
#     hover_data=["Compétence", "Domaine", "Matière"],
#     title=f"Position de la compétence “{comp_choice}” parmi toutes les compétences du réseau"
# )

# fig.add_hline(y=0, line_dash="dot")
# fig.add_vline(x=0, line_dash="dot")

# st.plotly_chart(fig, use_container_width=True)








# import streamlit as st
# import pandas as pd
# import numpy as np

# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans

# import plotly.express as px
# import plotly.graph_objects as go


# # ==========================================================
# # 1. CHARGEMENT DES DONNÉES
# # df : ton dataframe long déjà chargé dans l'app
# # ==========================================================

# st.title("🔍 Profilage des établissements")

# st.markdown("""
# Cette page identifie **des profils d’établissements** grâce à une analyse statistique avancée :

# - Nous calculons les **50 compétences moyennes** par établissement
# - Nous ajoutons la dynamique (**moyenne slope**, **moyenne spearman**)
# - Une réduction PCA permet de projeter les écoles en 3D
# - Un clustering **K-means (k=4)** identifie des *types d’établissements*
# """)

# df = st.session_state["df"]   # <-- ton dataframe global


# # ==========================================================
# # 2. CONSTRUCTION DES FEATURES POUR LE PROFILAGE
# # ==========================================================

# df_dyn = (
#     df.groupby(["Nom_ecole", "Compétence"])
#       .apply(lambda g: pd.Series({
#           "slope": evolution_slope(g),
#           "spearman": evolution_spearman(g),
#           "delta": delta_first_last(g),
#           "nb_niveaux": g["niveau_code"].nunique()
#       }))
#       .reset_index()
# )


# # 50 compétences en colonnes
# df_wide = df.pivot_table(
#     index="Nom_ecole",
#     columns="Compétence",
#     values="Valeur",
#     aggfunc="mean"
# )

# # Ajout dynamique slope / spearman
# df_dyn = (
#     df.groupby("Nom_ecole")
#       .agg({
#           "slope": "mean",
#           "spearman": "mean"
#       })
# )

# df = df.merge(df_dyn, on=["Nom_ecole", "Compétence"], how="left")


# df_feat = df_wide.join(df_dyn, how="left").fillna(0)

# st.subheader("🧩 Données utilisées pour le profilage")
# st.write(df_feat.head())


# # ==========================================================
# # 3. STANDARDISATION
# # ==========================================================

# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(df_feat)


# # ==========================================================
# # 4. PCA 3D
# # ==========================================================

# pca = PCA(n_components=3)
# X_pca = pca.fit_transform(X_scaled)

# df_pca = pd.DataFrame({
#     "PC1": X_pca[:, 0],
#     "PC2": X_pca[:, 1],
#     "PC3": X_pca[:, 2],
#     "Nom_ecole": df_feat.index
# })


# # ==========================================================
# # 5. K-MEANS (k=4)
# # ==========================================================

# k = 4
# kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
# df_pca["cluster"] = kmeans.fit_predict(X_scaled)

# df_feat["cluster"] = df_pca["cluster"].values


# st.subheader("🎨 Répartition des profils")
# st.write(df_pca["cluster"].value_counts())


# # ==========================================================
# # 6. AFFICHAGE 3D PLOTLY
# # ==========================================================

# st.subheader("🌐 Projection PCA 3D des établissements")

# fig = px.scatter_3d(
#     df_pca,
#     x="PC1",
#     y="PC2",
#     z="PC3",
#     color="cluster",
#     hover_name="Nom_ecole",
#     color_discrete_sequence=px.colors.qualitative.Set1,
#     title="Profilage des établissements — PCA (3D)"
# )

# fig.update_traces(marker=dict(size=6))
# fig.update_layout(height=700)

# st.plotly_chart(fig, use_container_width=True)


# # ==========================================================
# # 7. DESCRIPTION DES PROFILS
# # ==========================================================

# st.subheader("📘 Interprétation des profils")

# st.markdown("""
# **Profil 0 — Établissements fragiles mais homogènes**
# - Niveau global faible
# - Peu de différenciation entre compétences

# **Profil 1 — Établissements atypiques / extrêmes**
# - Très forts ou très faibles
# - Profils non standard

# **Profil 2 — Cœur du réseau**
# - Niveau correct à bon
# - Forces et faiblesses contrastées

# **Profil 3 — Défaillance ciblée**
# - Niveau global correct
# - Mais rupture sur une compétence / domaine
# """)


# # ==========================================================
# # 8. FICHE D’IDENTITÉ D’UN ÉTABLISSEMENT
# # ==========================================================

# st.subheader("🧬 Analyse d’un établissement")

# choix = st.selectbox("Choisir un établissement :", df_feat.index)

# st.markdown(f"### 🔎 Profil de : **{choix}**")

# st.write(f"**Cluster = {df_feat.loc[choix, 'cluster']}**")

# st.write("Scores moyens des compétences :")
# st.write(df_feat.loc[[choix]].drop(columns="cluster"))


import sys, os
import numpy as np
import pandas as pd
import streamlit as st

from scipy.stats import spearmanr, linregress
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import plotly.express as px
import plotly.graph_objects as go


# ==========================================================
# 0. CONFIG + IMPORT DES UTILITAIRES
# ==========================================================

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *
from fonctions_viz import *


# ==========================================================
# 1. CHARGEMENT DES DONNÉES DE SESSION
# ==========================================================

df = st.session_state.get("df")
df_coordo = st.session_state.get("df_coordo")

if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez d’abord la page Home.")
    st.stop()

df["Valeur"] = df["Valeur"] * 100

ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]
df["niveau_code"] = df["Niveau"].apply(lambda x: ordre_niveaux.index(x))


# ==========================================================
# 2. FONCTIONS STATISTIQUES
# ==========================================================

def evolution_slope(g):
    if g["niveau_code"].nunique() < 2:
        return np.nan
    slope, _, _, _, _ = linregress(g["niveau_code"], g["Valeur"])
    return slope

def evolution_spearman(g):
    if g["niveau_code"].nunique() < 2:
        return np.nan
    corr, _ = spearmanr(g["niveau_code"], g["Valeur"])
    return corr

def delta_first_last(g):
    if g["niveau_code"].nunique() < 2:
        return np.nan
    g = g.sort_values("niveau_code")
    return g["Valeur"].iloc[-1] - g["Valeur"].iloc[0]


# ==========================================================
# 3. INDICATEURS RÉSEAU
# ==========================================================

st.title("📊 Analyse réseau & Profilage des établissements")

st.subheader("Vue réseau – toutes les écoles")
st.markdown("""
## 🧠 Comprendre les indicateurs

- **Pente (slope)** : progression globale (positive = progresse, négative = baisse)
- **Spearman** : régularité de la progression (1 = régulier, 0 = irrégulier)
- **Idéal** : **pente positive + Spearman élevé**
""")

df_reseau = (
    df.groupby(["Matière", "Domaine", "Compétence", "Niveau"])
      ["Valeur"].mean()
      .reset_index()
)
df_reseau["niveau_code"] = df_reseau["Niveau"].apply(lambda x: ordre_niveaux.index(x))

# Calcul des indicateurs
df_evol_reseau = (
    df_reseau.groupby(["Matière", "Domaine", "Compétence"])
      .apply(lambda g: pd.Series({
          "slope": evolution_slope(g),
          "spearman": evolution_spearman(g),
          "delta": delta_first_last(g),
          "nb_niveaux": g["niveau_code"].nunique()
      }))
      .reset_index()
)

df_plot = df_evol_reseau[df_evol_reseau["nb_niveaux"] >= 2]


# ==========================================================
# 4. GRAPHIQUES GLOBAUX RÉSEAU
# ==========================================================

st.subheader("Distribution des pentes")
fig1 = px.histogram(df_plot, x="slope", color="Matière", nbins=25)
st.plotly_chart(fig1, use_container_width=True)

st.write("➡ À droite : progression forte — À gauche : régression.")

st.subheader("Progression vs régularité")
fig2 = px.scatter(
    df_plot,
    x="slope", y="spearman",
    color="Matière",
    hover_data=["Compétence", "Domaine"]
)
fig2.add_hline(y=0, line_dash="dot")
fig2.add_vline(x=0, line_dash="dot")
st.plotly_chart(fig2, use_container_width=True)

# Classements
st.header("🏆 Classements des compétences")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top progressions")
    st.dataframe(df_plot.sort_values("slope", ascending=False).head(10))

with col2:
    st.subheader("Top régressions")
    st.dataframe(df_plot.sort_values("slope", ascending=True).head(10))

st.subheader("Compétences les plus irrégulières")
st.dataframe(df_plot[df_plot["spearman"] < 0.3].sort_values("spearman").head(10))


# ==========================================================
# 5. EXPLORATION D’UNE COMPÉTENCE
# ==========================================================

st.header("🔍 Explorer une compétence en détail")

comp_choice = st.selectbox("Sélectionnez une compétence", df["Compétence"].unique())

df_comp = df_reseau[df_reseau["Compétence"] == comp_choice].sort_values("niveau_code")

fig3 = px.line(
    df_comp,
    x="Niveau", y="Valeur",
    markers=True,
    color="Niveau",
    title=f"Évolution de : {comp_choice}"
)
st.plotly_chart(fig3, use_container_width=True)


# ==========================================================
# 6. PROFILAGE DES ÉTABLISSEMENTS
# ==========================================================

st.title("🔍 Profilage des établissements")

st.markdown("""
Cette partie :
- crée 50 indicateurs compétences/école
- ajoute la dynamique (slope + spearman)
- applique une PCA 3D
- identifie 4 profils via **K-means**
""")

# ---- Construction des features ----

df_dyn = (
    df.groupby(["Nom_ecole", "Compétence"])
      .apply(lambda g: pd.Series({
          "slope": evolution_slope(g),
          "spearman": evolution_spearman(g),
      }))
      .reset_index()
)

df_dyn_global = df_dyn.groupby("Nom_ecole")[["slope", "spearman"]].mean()

df_wide = df.pivot_table(
    index="Nom_ecole", columns="Compétence", values="Valeur", aggfunc="mean"
)

df_feat = df_wide.join(df_dyn_global, how="left").fillna(0)

st.subheader("🧩 Données utilisées")
st.write(df_feat.head())

# ---- PCA ----
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_feat)

pca = PCA(n_components=3)
X_pca = pca.fit_transform(X_scaled)

df_pca = pd.DataFrame({
    "PC1": X_pca[:, 0],
    "PC2": X_pca[:, 1],
    "PC3": X_pca[:, 2],
    "Nom_ecole": df_feat.index
})

# ---- Clustering ----
k = 4
kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
df_pca["cluster"] = kmeans.fit_predict(X_scaled)
df_feat["cluster"] = df_pca["cluster"].values

st.subheader("🎨 Répartition des profils")
st.write(df_pca["cluster"].value_counts())

# ---- PCA 3D ----
fig = px.scatter_3d(
    df_pca, x="PC1", y="PC2", z="PC3",
    color="cluster", hover_name="Nom_ecole",
    color_discrete_sequence=px.colors.qualitative.Set1
)
fig.update_traces(marker=dict(size=6))
st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# 7. DESCRIPTION DES PROFILS
# ==========================================================

st.subheader("📘 Interprétation des profils")
st.markdown("""
**Profil 0 — Fragiles mais homogènes**
**Profil 1 — Atypiques / extrêmes**
**Profil 2 — Cœur du réseau, contrastés**
**Profil 3 — Défaillance ciblée**
""")


# ==========================================================
# 8. ANALYSE D’UN ÉTABLISSEMENT
# ==========================================================

st.subheader("🧬 Analyse d’un établissement")
choix = st.selectbox("Choisir un établissement :", df_feat.index)

st.markdown(f"### 🔎 Profil : **{choix}**")
st.write(f"**Cluster = {df_feat.loc[choix, 'cluster']}**")

st.write("Scores moyens des compétences :")
st.write(df_feat.loc[[choix]].drop(columns="cluster"))
