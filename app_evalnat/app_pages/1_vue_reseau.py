import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *
import matplotlib.pyplot as plt




st.header("Vue d’ensemble du réseau")

df = st.session_state.get('df')
df_coordo = st.session_state.get('df_coordo')

df['Valeur']=df['Valeur']*100


if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez la page Home")
    st.stop()

# ============================================
# SECTION 1 : Indicateurs clés
# ============================================

col1, col2, col3 = st.columns(3)

moy_globale = df["Valeur"].mean()
moy_maths = df.loc[df["Matière"] == "Mathématiques", "Valeur"].mean()
moy_fr = df.loc[df["Matière"] == "Français", "Valeur"].mean()
col1.metric("Moyenne générale", f"{moy_globale:.0f} %",border=True)
col2.metric("Mathématiques", f"{moy_maths:.0f}%",border=True)
col3.metric("Français", f"{moy_fr:.0f}%",border=True)




# fig = px.scatter_mapbox(
#     df_map,
#     lat="Lat",
#     lon="Long",
#     size="Moyenne",                  # Taille des points selon la moyenne
#     color="Moyenne",                 # Couleur selon la moyenne
#     hover_name="Nom_ecole",
#     hover_data={"Lat": False, "Long": False, "Moyenne": False,"Moyenne etab": True},
#     color_continuous_scale="Viridis",
#     zoom=1,
#     height=650
# )
# fig.update_layout(
#     mapbox_style="carto-positron",
#     mapbox_center={"lat": df_map["Lat"].mean(), "lon": df_map["Long"].mean()},
#     margin={"r":0, "t":0, "l":0, "b":0}
# )
# st.plotly_chart(fig, use_container_width=True)


# # st.subheader("Moyenne des résultats par matière et par niveau")

# # Calcul des moyennes par matière et niveau
# moyennes = (
#     df.groupby(["Matière", "Niveau"])["Valeur"]
#     .mean()
#     .reset_index()
#     .round(2)
# )

# # Forcer l’ordre des niveaux et trier
# moyennes["Niveau"] = pd.Categorical(moyennes["Niveau"], categories=ordre_niveaux, ordered=True)
# moyennes = moyennes.sort_values(["Matière", "Niveau"]).reset_index(drop=True)

# # Création du graphique
# fig = go.Figure()

# for matiere in moyennes["Matière"].unique():
#     df_mat = moyennes[moyennes["Matière"] == matiere].sort_values("Niveau")
#     fig.add_trace(
#         go.Scatter(
#             x=df_mat["Niveau"],
#             y=df_mat["Valeur"],
#             mode="lines+markers+text",
#             name=matiere,
#             line=dict(width=4, color=palette.get(matiere)),
#             marker=dict(size=10, line=dict(width=1, color="white")),
#             text=df_mat["Valeur"].round(2),
#             textposition="top center",
#         )
#     )


# # Mise en forme esthétique
# fig.update_layout(

#     xaxis=dict(
#         title="Niveau",
#         categoryorder="array",
#         categoryarray=ordre_niveaux,
#         tickfont=dict(size=13),
#     ),
#     yaxis=dict(
#         title="Score moyen",
#         tickfont=dict(size=13),
#         # 🔹 Resserre l’échelle autour des valeurs observées
#         range=[
#             moyennes["Valeur"].min() - 5,
#             moyennes["Valeur"].max() + 5
#         ],
#         dtick=5,
#     ),
#     legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y=1,
#         xanchor="center",
#         x=0.5,
#     ),

#     margin=dict(l=50, r=30, t=80, b=40),
# )
# st.plotly_chart(fig, use_container_width=True)


def heatmap_scores_par_reseau(df):
    """
    Affiche une carte de chaleur (heatmap) des scores moyens
    par réseau, matière et niveau scolaire.
    """


    colonnes_requises = {'Niveau', 'Matière', 'Valeur', 'Réseau'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir : Niveau, Matière, Valeur, Réseau.")
        return

    # Filtrer uniquement les matières principales
    df_filtre = df[df["Matière"].isin(["Français", "Mathématiques"])].copy()

    # Choix de la matière à afficher
    matiere = st.segmented_control(
        "Choisissez la matière à afficher :",
        ["Français", "Mathématiques"],
        selection_mode="single",
        default="Français"
    )

    # Calcul des moyennes par réseau et niveau
    grouped = (
        df_filtre[df_filtre["Matière"] == matiere]
        .groupby(["Réseau", "Niveau"], as_index=False)["Valeur"]
        .mean()
        .round(1)
    )
    grouped["Niveau"] = pd.Categorical(grouped["Niveau"], categories=ordre_niveaux, ordered=True)

    # Pivot pour le heatmap : Réseaux en lignes, Niveaux en colonnes
    pivot = grouped.pivot(index="Réseau", columns="Niveau", values="Valeur")

    # --- Graphique Plotly ---
    fig = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        text_auto=True,
        aspect="auto",
        labels=dict(color="Score moyen"),
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_colorbar=dict(title="Score"),
        height=225,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}# 🔹 fixe la hauteur de la figure
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig

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
                textposition="top center",
            )
        )

    fig.update_layout(
        height=300,
        xaxis=dict(
            categoryarray=ordre_niveaux,
            ),
        yaxis=dict(
            range=[moyennes["Valeur"].min() - 5, moyennes["Valeur"].max() + 5],
            ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5,
            ),
        margin=dict(l=50, r=30, t=0, b=0),
        )
    return fig


def afficher_moyennes_par_domaine(df):
    """Un seul graphique combinant Français (bleu) et Mathématiques (orange/rouge)."""

    # --- Préparation des données ---
    df = df.dropna(subset=["Matière", "Domaine", "Statut", "Valeur"])
    df_domaine = (
        df.groupby(["Matière", "Domaine", "Statut"], as_index=False)
        .agg(Moyenne=("Valeur", "mean"))
    )

    # --- Ordre des domaines (Français à gauche, Math à droite) ---
    domaines_fr = df_domaine[df_domaine["Matière"] == "Français"]["Domaine"].unique().tolist()
    domaines_math = df_domaine[df_domaine["Matière"] == "Mathématiques"]["Domaine"].unique().tolist()
    df_domaine["Domaine"] = pd.Categorical(df_domaine["Domaine"], categories=domaines_fr + domaines_math, ordered=True)

    # --- Couleurs déclinées par matière/statut ---
    statuts = sorted(df_domaine["Statut"].unique())
    declinaisons_fr = ["#002b5c", "#0056b3", "#99b9f2"]   # Bleu foncé → clair
    declinaisons_math = ["#8B1A1A", "#E74C3C", "#F5B7B1"] # Rouge foncé → clair

    color_map = {}
    for i, s in enumerate(statuts):
        color_map[f"Français-{s}"] = declinaisons_fr[i]
        color_map[f"Mathématiques-{s}"] = declinaisons_math[i]

    # --- Fusion matière + statut pour color mapping ---
    df_domaine["Catégorie"] = df_domaine["Matière"] + "-" + df_domaine["Statut"]

    # --- Graphique combiné ---
    fig = px.bar(
        df_domaine,
        x="Domaine",
        y="Moyenne",
        color="Catégorie",
        barmode="group",
        color_discrete_map=color_map,
        height=450
    )

    # --- Mise en forme ---
    fig.update_traces(marker_line_width=0.5, marker_line_color="white")
    fig.update_layout(
        showlegend=True,
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=40, r=20, t=60, b=100),
        bargap=0.25,
    )

    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def afficher_top_bottom(df):
    """
    Affiche deux DataFrames :
      - Le Top 3 selon la valeur moyenne
      - Le Bottom 3 juste en dessous
    L'utilisateur choisit le niveau d'analyse (Nom de l'école, Domaine, Compétence).
    """

    # Vérification des colonnes nécessaires
    colonnes_requises = {'Nom_ecole', 'Domaine', 'Compétence', 'Valeur'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir les colonnes : Nom_ecole, Domaine, Compétence, Valeur.")
        return

    # Labels lisibles pour l'utilisateur
    labels = {
        "École": "Nom_ecole",
        "Domaine": "Domaine",
        "Compétence": "Compétence"
    }

    # Contrôle segmenté
    choix_label = st.segmented_control(
        "Choisissez le niveau d'analyse :",
        list(labels.keys()),
        selection_mode="single",
        default="École"
    )

    # Récupération du vrai nom de colonne
    choix = labels[choix_label]

    # Calcul des moyennes
    grouped = df.groupby(choix, as_index=False)["Valeur"].mean().round(2)
    grouped = grouped.sort_values(by="Valeur", ascending=False)
    grouped = grouped.rename(columns={'Nom_ecole': 'École'})


    # Séparation top / bottom 3
    top3 = grouped.head(3).reset_index(drop=True)
    bottom3 = grouped.tail(3).sort_values(by="Valeur", ascending=True).reset_index(drop=True)

    # --- AFFICHAGE ---
    st.write(f"**Top 3 {choix_label.lower()}s**")
    st.dataframe(top3, use_container_width=True)

    st.write(f" **Bottom 3 {choix_label.lower()}s**")
    st.dataframe(bottom3, use_container_width=True)


# def graphique_moyenne_ou_ecart(df):
#         """
#         Affiche un graphique en barres interactif (Plotly)
#         permettant de visualiser soit les écarts à la moyenne globale,
#         soit les moyennes brutes pour Français et Mathématiques,
#         selon le critère choisi (Réseau, Statut, Homologué).
#         """

#         colonnes_requises = {'Matière', 'Valeur', 'Réseau', 'Statut', 'Homologué'}
#         if not colonnes_requises.issubset(df.columns):
#             st.error("Le DataFrame doit contenir : Matière, Valeur, Réseau, Statut, Homologué.")
#             return

#         # Filtrage des matières
#         df_filtre = df[df["Matière"].isin(["Français", "Mathématiques"])].copy()

#         col1, col2 = st.columns([1, 1])

#         # Choix du critère d'analyse
#         with col1 :
#             critere = st.segmented_control(
#                 "Choisissez le critère d'analyse :",
#                 ["Réseau", "Statut", "Homologué"],
#                 selection_mode="single",
#                 default="Réseau"
#             )

#         # --- TOGGLE entre moyennes et écarts ---
#         with col2:
#             afficher_ecarts = st.toggle("Afficher les écarts à la moyenne globale", value=True)

#         # Moyenne globale (pour calculer les écarts)
#         moyenne_globale = df_filtre["Valeur"].mean()

#         # Calcul de la moyenne par groupe
#         grouped = (
#             df_filtre.groupby([critere, "Matière"], as_index=False)["Valeur"]
#             .mean()
#             .rename(columns={"Valeur": "Moyenne"})
#         )

#         if afficher_ecarts:
#             grouped["Valeur_affichée"] = grouped["Moyenne"] - moyenne_globale
#             titre_y = "Écart à la moyenne globale"

#         else:
#             grouped["Valeur_affichée"] = grouped["Moyenne"]
#             titre_y = "Moyenne"


#         # --- Graphique Plotly ---
#         fig = px.bar(
#             grouped,
#             x=critere,
#             y="Valeur_affichée",
#             color="Matière",
#             barmode="group",
#             text="Valeur_affichée",
#             color_discrete_map=palette)

#         # Ligne de référence à 0 uniquement si on affiche les écarts
#         if afficher_ecarts:
#             fig.add_hline(y=0, line_dash="dash", line_color="gray")

#         # Mise en forme
#         fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
#         fig.update_layout(
#             yaxis_title=titre_y,
#             xaxis_title=critere,
#             plot_bgcolor="white",
#             bargap=0.3,
#             showlegend=True,
#             height=350
#         )

#         st.plotly_chart(fig, use_container_width=True)

def graphique_moyenne_ou_ecart(df, palette):
    """
    Affiche un graphique combiné avec 3 sous-graphes (Réseau, Statut, Homologué),
    chacun ayant ses propres catégories en abscisse.
    L'utilisateur peut basculer entre moyennes et écarts via un toggle.
    """


    colonnes_requises = {'Matière', 'Valeur', 'Réseau', 'Statut', 'Homologué'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir : Matière, Valeur, Réseau, Statut, Homologué.")
        return

    # Filtrer uniquement Français et Mathématiques
    df_filtre = df[df["Matière"].isin(["Français", "Mathématiques"])].copy()

    # --- TOGGLE entre moyennes et écarts ---
    afficher_ecarts = st.toggle("Afficher les écarts à la moyenne globale", value=True)

    # Moyenne globale pour le calcul des écarts
    moyenne_globale = df_filtre["Valeur"].mean()

    # --- Construction du dataframe long regroupant les 3 critères ---
    df_long = pd.concat([
        df_filtre[["Matière", "Valeur", "Réseau"]].rename(columns={"Réseau": "Critère_valeur"}).assign(Critère="Réseau"),
        df_filtre[["Matière", "Valeur", "Statut"]].rename(columns={"Statut": "Critère_valeur"}).assign(Critère="Statut"),
        df_filtre[["Matière", "Valeur", "Homologué"]].rename(columns={"Homologué": "Critère_valeur"}).assign(Critère="Homologué")
    ])

    # Moyenne par (Critère, valeur, matière)
    grouped = (
        df_long.groupby(["Critère", "Critère_valeur", "Matière"], as_index=False)["Valeur"]
        .mean()
        .rename(columns={"Valeur": "Moyenne"})
    )

    # Valeur à afficher : moyenne ou écart
    if afficher_ecarts:
        grouped["Valeur_affichée"] = grouped["Moyenne"] - moyenne_globale
        titre_y = "Écart à la moyenne globale"
    else:
        grouped["Valeur_affichée"] = grouped["Moyenne"]
        titre_y = "Moyenne"

    # --- Graphique combiné ---
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

    fig.update_xaxes(title_text=None)


    # Ligne de référence à 0 uniquement pour les écarts
    if afficher_ecarts:
        fig.add_hline(y=0, line_dash="dash", line_color="gray")

    # --- Mise en forme ---
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        yaxis_title=titre_y,
        xaxis_title=None,
        plot_bgcolor="white",
        bargap=0.3,
        showlegend=True,
        height=450,
    )


    # 🔹 Axes indépendants
    fig.for_each_xaxis(lambda ax: ax.update(matches=None))
    fig.for_each_xaxis(
    lambda ax: ax.update(tickangle=45) if "Réseau" in ax.anchor else None
)


    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))  # nettoyer le titre des facettes

    st.plotly_chart(fig, use_container_width=True)


# Deux colonnes Streamlit
col1, col2 = st.columns([2, 1])

with col1:
    # st.subheader("Carte des établissements")
    with st.container(border=True):
        df_map = prepare_map_data(df, df_coordo)
        fig_map = plot_map(df_map)
        st.plotly_chart(fig_map, use_container_width=True)

with col2:
    with st.container(border=True):
        afficher_top_bottom(df)




col1, col2=st.columns(2)

with col1:
    with st.container(border=True):

        # afficher_moyennes_par_domaine(df)
        heatmap_scores_par_reseau(df)

with col2 :

    with st.container(border=True):

        fig_line = plot_line_chart(df, palette, ordre_niveaux)
        st.plotly_chart(fig_line, use_container_width=True)

with st.container(border=True):
    graphique_moyenne_ou_ecart(df,palette)


# col1, col2, col3 =st.columns(3)

# with col1:
#     with st.container(border=True):
#         # afficher_moyennes_par_domaine(df)
#         heatmap_scores_par_reseau(df)

# with col2 :
#     with st.container(border=True):
#         fig_line = plot_line_chart(df, palette, ordre_niveaux)
#         st.plotly_chart(fig_line, use_container_width=True)

# with col3 :
#     with st.container(border=True):
#         graphique_moyenne_ou_ecart(df)
