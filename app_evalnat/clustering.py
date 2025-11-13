# ============================================
# Fichier : pai_clustering.py
# ============================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import linregress, spearmanr
import random

np.random.seed(42)
random.seed(42)

# --------------------------------------------
# 1. Fonctions utilitaires statistiques
# --------------------------------------------

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

# --------------------------------------------
# 2. Construction du DataFrame de features
# --------------------------------------------

def construire_features(df):
    """
    Retourne un DF large (compétences en colonnes) + slope + spearman.
    df doit contenir : Nom_ecole, Compétence, Valeur, niveau_code
    """

    # dynamiques
    df_dyn = (
        df.groupby(["Nom_ecole", "Compétence"])
          .apply(lambda g: pd.Series({
              "slope": evolution_slope(g),
              "spearman": evolution_spearman(g)
          }))
          .reset_index()
    )

    df_dyn_global = df_dyn.groupby("Nom_ecole")[["slope", "spearman"]].mean()

    # pivot compétences
    df_wide = df.pivot_table(
        index="Nom_ecole",
        columns="Compétence",
        values="Valeur",
        aggfunc="mean"
    )

    # dataset final
    df_feat = df_wide.join(df_dyn_global, how="left").fillna(0)

    return df_feat

# --------------------------------------------
# 3. PCA + Clustering (KMeans)
# --------------------------------------------

def calculer_clustering(df_feat, n_clusters=4):
    """
    Retourne :
    - df_feat enrichi du cluster
    - df_pca (coordonnées PCA + cluster)
    """

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_feat)

    pca = PCA(n_components=3)
    coords = pca.fit_transform(X_scaled)

    df_pca = pd.DataFrame({
        "Nom_ecole": df_feat.index,
        "PC1": coords[:,0],
        "PC2": coords[:,1],
        "PC3": coords[:,2]
    })

    kmeans = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
    df_pca["cluster"] = kmeans.fit_predict(X_scaled)

    df_feat = df_feat.copy()
    df_feat["cluster"] = df_pca["cluster"].values

    return df_feat, df_pca, pca, scaler, kmeans

# df = st.session_state.get('df')
# df_coordo = st.session_state.get('df_coordo')

# if df is None or df.empty:
#     st.warning("Aucune donnée disponible. Ouvrez la page Home")
#     st.stop()

# df['Valeur'] = df['Valeur'] * 100
# df_feat = construire_features(df)
# df_feat, df_pca, pca, scaler, kmeans = calculer_clustering(df_feat)

# --------------------------------------------
# 4. Descriptions textuelles des clusters
# --------------------------------------------

DESCRIPTIONS_PROFILS = {
    0: "Établissements fragiles mais homogènes.",
    1: "Établissements atypiques / extrêmes.",
    2: "Cœur du réseau — bons résultats mais contrastés.",
    3: "Défaillance ciblée — résultats corrects mais points faibles nets."
}

def description_profil(cluster_id: int) -> str:
    return DESCRIPTIONS_PROFILS.get(cluster_id+1, "Profil non identifié.")
