import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import spearmanr
from config import *



# =============================
# Page : vue_reseau.py
# =============================

def get_moyenne_et_delta(df_global, df_ecole, matiere=None):
    """
    Calcule la moyenne de l'établissement et le delta par rapport à la moyenne réseau.

    Paramètres :
    -----------
    df_global : DataFrame complet du réseau
    df_ecole  : DataFrame filtré pour l'établissement sélectionné
    matiere   : str ou None
                "Mathématiques", "Français" ou None (pour la moyenne générale)

    Retourne :
    ----------
    (moyenne_ecole, delta) sous forme de tuple (float, float)
    """

    if matiere:
        # Moyenne pour la matière sélectionnée
        moy_ecole = df_ecole.loc[df_ecole["Matière"] == matiere, "Valeur"].mean()
        moy_reseau = df_global.loc[df_global["Matière"] == matiere, "Valeur"].mean()
    else:
        # Moyenne générale
        moy_ecole = df_ecole["Valeur"].mean()
        moy_reseau = df_global["Valeur"].mean()

    delta = moy_ecole - moy_reseau
    return moy_ecole, delta


def heatmap_scores_par_reseau(df, ordre_niveaux):
    """Affiche une heatmap des scores moyens par réseau et par niveau."""
    colonnes_requises = {'Niveau', 'Matière', 'Valeur', 'Réseau'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir : Niveau, Matière, Valeur, Réseau.")
        return

    df_filtre = df[df["Matière"].isin(["Français", "Mathématiques"])].copy()

    matiere = st.segmented_control(
        "Choisissez la matière à afficher :",
        ["Français", "Mathématiques"],
        selection_mode="single",
        default="Français"
    )

    grouped = (
        df_filtre[df_filtre["Matière"] == matiere]
        .groupby(["Réseau", "Niveau"], as_index=False)["Valeur"]
        .mean()
        .round(1)
    )
    grouped["Niveau"] = pd.Categorical(grouped["Niveau"], categories=ordre_niveaux, ordered=True)

    pivot = grouped.pivot(index="Réseau", columns="Niveau", values="Valeur")

    fig = px.imshow(
        pivot,
        color_continuous_scale="Viridis",
        text_auto=True,
        aspect="auto",
        labels=dict(color="Score moyen"),
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_colorbar=dict(title="Score"),
        margin=dict(l=40, r=20, t=10, b=40),
        height=225,
    )

    st.plotly_chart(fig, use_container_width=True)


def prepare_map_data(df, df_coordo):
    """Calcule la moyenne des valeurs par école et fusionne avec les coordonnées."""
    df_mean = df.groupby("Nom_ecole", as_index=False)["Valeur"].mean()
    df_map = pd.merge(df_mean, df_coordo, on="Nom_ecole", how="left")
    df_map = df_map.rename(columns={'Valeur': 'Moyenne'})
    df_map["Moyenne etab"] = df_map["Moyenne"].map(lambda x: f"{x:.2f} %")
    df_map = df_map.dropna()
    return df_map


def plot_map(df_map):
    """Affiche la carte interactive des établissements."""
    fig = px.scatter_mapbox(
        df_map,
        lat="Lat",
        lon="Long",
        size="Moyenne",
        color="Moyenne",
        hover_name="Nom_ecole",
        hover_data={"Lat": False, "Long": False, "Moyenne": False, "Moyenne etab": True},
        color_continuous_scale="Viridis",
        zoom=1,
        height=474
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": df_map["Lat"].mean(), "lon": df_map["Long"].mean()},
        margin=dict(l=40, r=20, t=10, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_line_chart(df, palette, ordre_niveaux):
    """Trace la moyenne des résultats par matière et par niveau."""
    moyennes = (
        df.groupby(["Matière", "Niveau"])["Valeur"]
        .mean()
        .reset_index()
        .round(2)
    )
    moyennes["Niveau"] = pd.Categorical(moyennes["Niveau"], categories=ordre_niveaux, ordered=True)
    moyennes = moyennes.sort_values(["Matière", "Niveau"]).reset_index(drop=True)

    fig = go.Figure()
    for matiere in moyennes["Matière"].unique():
        df_mat = moyennes[moyennes["Matière"] == matiere].sort_values("Niveau")
        fig.add_trace(
            go.Scatter(
                x=df_mat["Niveau"],
                y=df_mat["Valeur"],
                mode="lines+markers+text",
                name=matiere,
                line=dict(width=4, color=palette.get(matiere, "#888")),
                marker=dict(size=10, line=dict(width=1, color="white")),
                text=df_mat["Valeur"].round(2),
                texttemplate="%{text:.2f}",
                textposition="top center",
            )
        )

    fig.update_layout(
        height=300,
        xaxis=dict(categoryarray=ordre_niveaux),
        yaxis=dict(
            title="Score moyen",
            range=[moyennes["Valeur"].min() - 5, moyennes["Valeur"].max() + 5]
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5),
        margin=dict(l=40, r=20, t=10, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def afficher_top_bottom(df):
    """Affiche Top 3 et Bottom 3 selon la valeur moyenne, par niveau d’analyse choisi."""
    colonnes_requises = {'Domaine', 'Compétence', 'Valeur'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir les colonnes : Nom_ecole, Domaine, Compétence, Valeur.")
        return

    labels = {"Domaine": "Domaine", "Compétence": "Compétence"}

    choix_label = st.segmented_control(
        "Choisissez le niveau d'analyse :",
        list(labels.keys()),
        selection_mode="single",
        default="Domaine"
    )

    choix = labels[choix_label]

    grouped = df.groupby(choix, as_index=False)["Valeur"].mean().round(2)
    grouped = grouped.sort_values(by="Valeur", ascending=False)
    # grouped = grouped.rename(columns={'Nom_ecole': 'École'})

    top3 = grouped.head(3).reset_index(drop=True)
    bottom3 = grouped.tail(3).sort_values(by="Valeur", ascending=True).reset_index(drop=True)

    st.write(f"**Top 3 {choix_label.lower()}s**")
    st.dataframe(top3, use_container_width=True)

    st.write(f"**Bottom 3 {choix_label.lower()}s**")
    st.dataframe(bottom3, use_container_width=True)


def graphique_moyenne_ou_ecart(df, palette):
    """Graphique combiné multi-critères avec toggle écarts/moyennes."""
    colonnes_requises = {'Matière', 'Valeur', 'Réseau', 'Statut', 'Homologué'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir : Matière, Valeur, Réseau, Statut, Homologué.")
        return

    df_filtre = df[df["Matière"].isin(["Français", "Mathématiques"])].copy()
    afficher_ecarts = st.toggle("Afficher les écarts à la moyenne globale", value=True)
    moyenne_globale = df_filtre["Valeur"].mean()

    df_long = pd.concat([
        df_filtre[["Matière", "Valeur", "Réseau"]].rename(columns={"Réseau": "Critère_valeur"}).assign(Critère="Réseau"),
        df_filtre[["Matière", "Valeur", "Statut"]].rename(columns={"Statut": "Critère_valeur"}).assign(Critère="Statut"),
        df_filtre[["Matière", "Valeur", "Homologué"]].rename(columns={"Homologué": "Critère_valeur"}).assign(Critère="Homologué")
    ])

    grouped = (
        df_long.groupby(["Critère", "Critère_valeur", "Matière"], as_index=False)["Valeur"]
        .mean()
        .rename(columns={"Valeur": "Moyenne"})
    )

    if afficher_ecarts:
        grouped["Valeur_affichée"] = grouped["Moyenne"] - moyenne_globale
        titre_y = "Écart à la moyenne globale"
    else:
        grouped["Valeur_affichée"] = grouped["Moyenne"]
        titre_y = "Moyenne"

    fig = px.bar(
        grouped,
        x="Critère_valeur",
        y="Valeur_affichée",
        color="Matière",
        facet_col="Critère",
        barmode="group",
        text="Valeur_affichée",
        color_discrete_map=palette
    )

    if afficher_ecarts:
        fig.add_hline(y=0, line_dash="dash", line_color="gray")

    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        yaxis_title=titre_y,
        xaxis_title=None,
        plot_bgcolor="white",
        bargap=0.3,
        showlegend=True,
        margin=dict(l=40, r=20, t=20, b=40),
        height=450,
        legend=dict(
            title=None,
            orientation="h",       # horizontale
            yanchor="bottom",
            y=1.15,                # légèrement au-dessus du graphe
            xanchor="center",
            x=0.5
        ),
    )

   # Supprime les labels/ticks de l’axe X
    fig.for_each_xaxis(lambda ax: ax.update(showticklabels=False, title_text=None, matches=None))

    # Nettoyage des titres de facettes ("Critère=Réseau" → "Réseau")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    st.plotly_chart(fig, use_container_width=True)



# =============================
# Page : vue_etablissement.py
# =============================


def plot_radar_domaine(df_ecole, df_global, ecole_selectionnee, palette):
    """
    Affiche un radar unique combinant tous les domaines (Français + Mathématiques)
    pour un établissement donné, comparé à la moyenne du réseau.
    Utilise plotly.express.line_polar pour un rendu fluide et homogène.
    """

    # --- Calcul des moyennes par matière et domaine ---
    df_ecole_mean = (
        df_ecole.groupby(["Matière", "Domaine"])["Valeur"]
        .mean()
        .reset_index()
    )
    df_reseau_mean = (
        df_global.groupby(["Matière", "Domaine"])["Valeur"]
        .mean()
        .reset_index()
    )

    # --- Ajout du type pour distinguer établissement / réseau ---
    df_ecole_mean["Type"] = f"{ecole_selectionnee}"
    df_reseau_mean["Type"] = "Moyenne réseau"

    df_radar = pd.concat([df_ecole_mean, df_reseau_mean], axis=0)

    # --- Domaine complet = "Matière - Domaine" ---
    df_radar["Domaine complet"] = df_radar["Matière"] + " - " + df_radar["Domaine"]

    # --- Couleurs : palette issue de config ---
    color_map = {
        f"{ecole_selectionnee}": palette["Français"],  # couleur de base, on ajustera ensuite
        "Moyenne réseau": palette["Moyenne réseau"],
    }

    # --- Construction du radar ---
    fig = px.line_polar(
        df_radar,
        r="Valeur",
        theta="Domaine complet",
        color="Type",
        line_close=True,
        markers=True,
        color_discrete_map=color_map,

    )



    # --- Mise en forme Plotly ---
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 20, 40, 60, 80, 100],
                tickfont=dict(size=10),
            )
        ),
        legend_title_text=None,
        showlegend=True,
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_traces(fill='toself')


    st.plotly_chart(fig, use_container_width=True)


def plot_heatmap_competences(df_ecole,ordre_niveaux):
    """Affiche la carte de chaleur des compétences selon le niveau."""
    matiere = st.segmented_control(
        "Choisissez la matière :", ["Français", "Mathématiques"], default="Français"
    )

    df_mat = df_ecole[df_ecole["Matière"] == matiere]

    grouped = (
        df_mat.groupby(["Compétence", "Niveau"])["Valeur"]
        .mean()
        .reset_index()
    )
    grouped["Niveau"] = pd.Categorical(grouped["Niveau"], categories=ordre_niveaux, ordered=True)

    if grouped.empty:
        st.warning("Pas de données suffisantes pour cet établissement.")
        return

    pivot = grouped.pivot(index="Compétence", columns="Niveau", values="Valeur")

    fig = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        text_auto=".1f",
        aspect="auto",
        labels=dict(color="Score moyen (%)")
    )

    fig.update_layout(height=500, margin=dict(l=40, r=40, t=20, b=40))
    st.plotly_chart(fig, use_container_width=True)




def plot_scatter_comparatif(df, ecole_selectionnee):
    """Compare les établissements sur la moyenne Math vs Français avec régression."""

    # On calcule la moyenne par établissement et matière
    df_m = (
        df.groupby(["Nom_ecole", "Matière"])["Valeur"]
        .mean()
        .unstack()
        .reset_index()
    )

    # Renommer les colonnes si besoin
    if "Français" not in df_m.columns or "Mathématiques" not in df_m.columns:
        st.warning("Les données sont incomplètes (une matière manquante). Impossible d’afficher la comparaison.")
        return

    # Supprimer les écoles sans les deux matières
    df_m = df_m.dropna(subset=["Français", "Mathématiques"])

    if df_m.empty:
        st.warning("Aucune donnée suffisante pour générer le graphique comparatif.")
        return

    # Création du scatter général
    fig = px.scatter(
        df_m,
        x="Mathématiques",
        y="Français",
        opacity=0.6,
        color_discrete_sequence=["#999999"],
        title="Comparaison des établissements",
        trendline="ols",
    )

    # Mise en avant de l’établissement sélectionné
    df_sel = df_m[df_m["Nom_ecole"] == ecole_selectionnee]
    if not df_sel.empty:
        fig.add_trace(go.Scatter(
            x=df_sel["Mathématiques"],
            y=df_sel["Français"],
            mode="markers+text",
            text=df_sel["Nom_ecole"],
            textposition="top center",
            marker=dict(size=14, color="#e74c3c", line=dict(width=2, color="white")),
            name=ecole_selectionnee,
        ))
    else:
        st.info("⚠️ L’établissement sélectionné n’a pas de données complètes pour ce graphique.")

    # Mise en forme
    fig.update_layout(
        height=450,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_title="Moyenne Mathématiques (%)",
        yaxis_title="Moyenne Français (%)",
        plot_bgcolor="white",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


# def plot_bar_classement(df, ecole_selectionnee):
#     choix_vue = st.segmented_control(
#         "Choisissez la vue :", ["Moyenne générale", "Mathématiques", "Français"], default="Moyenne générale"
#     )

#     if choix_vue == "Moyenne générale":
#         grouped = df.groupby("Nom_ecole")["Valeur"].mean().reset_index()
#     else:
#         grouped = df[df["Matière"] == choix_vue].groupby("Nom_ecole")["Valeur"].mean().reset_index()

#     grouped = grouped.sort_values(by="Valeur", ascending=False)
#     grouped["Couleur"] = np.where(grouped["Nom_ecole"] == ecole_selectionnee, "#e74c3c", "#888")

#     fig = px.bar(
#         grouped,
#         x="Nom_ecole",
#         y="Valeur",
#         text="Valeur",
#         color="Couleur",
#         color_discrete_map="identity",
#     )

#     fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
#     fig.update_layout(
#         height=450,
#         margin=dict(l=40, r=40, t=40, b=40),
#         showlegend=False,
#         xaxis_title=None,
#         yaxis_title="Score moyen (%)",
#     )

#     st.plotly_chart(fig, use_container_width=True)





