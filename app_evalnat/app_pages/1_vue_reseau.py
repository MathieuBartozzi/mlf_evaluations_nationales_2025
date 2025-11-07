import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *



st.header("Vue d’ensemble du réseau")

df = st.session_state.get('df')
df_coordo = st.session_state.get('df_coordo')

df['Valeur']=df['Valeur']*100


if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez la page Home")
    st.stop()

# col1, col2=st.columns(2)
# col1.dataframe(df)
# col2.dataframe(df_coordo)


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


# # ============================================
# # Ligne 2 : Cartographie
# # ============================================

# # Moyenne des valeurs par école
# df_mean = df.groupby("Nom_ecole", as_index=False)["Valeur"].mean()
# # Fusion des moyennes avec les coordonnées géographiques
# df_map = pd.merge(
#     df_mean,
#     df_coordo,
#     on="Nom_ecole",
#     how="left"
# )
# df_map = df_map.rename(columns={'Valeur': 'Moyenne'})
# df_map["Moyenne etab"] = df_map["Moyenne"].map(lambda x: f"{x:.2f} %")
# df_map = df_map.dropna()



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
        height=700
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
        height=250,
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

# Deux colonnes Streamlit
col1, col2 = st.columns([1, 1])

with col1:
    # st.subheader("Carte des établissements")
    df_map = prepare_map_data(df, df_coordo)
    fig_map = plot_map(df_map)
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    # st.subheader("Évolution des résultats")
    fig_line = plot_line_chart(df, palette, ordre_niveaux)
    st.plotly_chart(fig_line, use_container_width=True)

    afficher_moyennes_par_domaine(df)




# --- Fonction 1 : Moyennes par homologation ---
def afficher_comparaison_homologation(df):
    """Affiche la moyenne générale selon l’homologation (graphique simple et compact)."""

    # --- Nettoyage ---
    df = df.dropna(subset=["Homologué", "Valeur"])
    df["Homologué"] = df["Homologué"].astype(str).str.lower().str.strip()

    # --- Moyenne générale par groupe ---
    df_moyennes = (
        df.groupby("Homologué")["Valeur"]
        .mean()
        .reset_index(name="Moyenne générale")
    )

    # --- Ordre et étiquettes cohérents ---
    df_moyennes["Homologué"] = pd.Categorical(
        df_moyennes["Homologué"], categories=["oui", "non"], ordered=True
    )


    # --- Graphique ---
    fig = px.bar(
        df_moyennes,
        x="Homologué",
        y="Moyenne générale",
        color="Homologué",
        color_discrete_map=palette,
        text_auto=".1f",
        title="Moyenne générale selon l’homologation",
    )

    # --- Mise en forme compacte et esthétique ---
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12),
        marker_line_width=0.8,
        marker_line_color="white"
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(range=[df_moyennes["Moyenne générale"].min() - 5,
                          df_moyennes["Moyenne générale"].max() + 5]),
        xaxis=dict(
            tickvals=["oui", "non"],
            ticktext=["Homologué", "Non homologué"]
        ),
        margin=dict(l=30, r=30, t=50, b=40),
        height=300,  # 🔹 plus compact
        font=dict(size=13),
        title=dict(font=dict(size=15), x=0.05, y=0.9)
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Fonction 2 : Dispersion globale par homologation ---
def afficher_dispersion_globale_homologation(df):
    """Affiche la dispersion globale des valeurs selon l’homologation."""

    # --- Nettoyage ---
    df = df.dropna(subset=["Homologué", "Valeur"])
    df["Homologué"] = df["Homologué"].astype(str).str.lower().str.strip()
    df = df[df["Homologué"].isin(["oui", "non"])]

    # --- Graphique Violin ---
    fig = px.violin(
        df,
        x="Homologué",
        y="Valeur",
        color="Homologué",
        box=True,
        points="all",
        color_discrete_map=palette,
        hover_data=["Matière", "Compétence", "Nom_ecole"],
        title="Distribution globale des valeurs selon l’homologation",
    )

    fig.update_traces(
        meanline_visible=True,
        opacity=0.7,
        marker=dict(size=3)
    )
    fig.update_layout(
        showlegend=False,
        yaxis_title=None,
        xaxis_title=None,
        height=420,
        margin=dict(l=40, r=40, t=80, b=60),
        font=dict(size=13),
    )

    st.plotly_chart(fig, use_container_width=True)


# --- Affichage côte à côte (correction du bug Streamlit) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Effet de l’homologation")
    afficher_comparaison_homologation(df)
    afficher_dispersion_globale_homologation(df)

with col2:
    st.subheader("Fr vs maths")


# # --- Filtres via st.pills ---
# reseaux = sorted(df["Réseau"].dropna().unique())
# statuts = sorted(df["Statut"].dropna().unique())
# homologations = sorted(df["Homologué"].dropna().unique())


# reseau_sel = st.pills("Réseau", reseaux, selection_mode="multi")
# statut_sel = col2.pills("Statut", statuts, selection_mode="multi")
# homo_sel = col3.pills("Homologué", homologations, selection_mode="multi")

# # --- Application des filtres (directement sur df) ---
# mask = pd.Series(True, index=df.index)

# mask &= df["Réseau"].isin(reseau_sel)

# if statut_sel:
#     mask &= df["Statut"].isin(statut_sel)
# if homo_sel:
#     mask &= df["Homologué"].isin(homo_sel)

# df_filtered = df[mask]

# # --- Calcul des moyennes par domaine ---
# df_domaine = (
#     df_filtered.groupby("Domaine", as_index=False)
#     .agg(Moyenne=("Valeur", "mean"))
#     .sort_values("Moyenne", ascending=False)
# )

# # --- Affichage du bar chart ---
# if df_domaine.empty:
#     st.warning("Aucune donnée ne correspond à cette sélection.")
# else:
#     fig_bar = px.bar(
#         df_domaine,
#         x="Moyenne",
#         y="Domaine",
#         orientation="h",
#         color="Moyenne",
#         color_continuous_scale="RdYlGn",
#         title="Moyenne par domaine"
#     )
#     fig_bar.update_layout(
#         xaxis_title="Moyenne",
#         yaxis_title="Domaine",
#         height=600,
#         margin=dict(l=0, r=0, t=40, b=0)
#     )
#     st.plotly_chart(fig_bar, use_container_width=True)

# colmap, colbar = st.columns([1.2, 1])



# # ---- Top / Bottom 3 compétences ----
# st.markdown("### 🏅 Compétences remarquables")

# df_comp_all = (
#     df_filtre.groupby("Compétence", as_index=False)
#     .agg(
#         Moyenne=("Valeur", "mean"),
#         Niveaux=("Niveau", lambda x: ", ".join(sorted(set(x))))
#     )
#     .sort_values("Moyenne", ascending=False)
# )

# top3 = df_comp_all.head(3)
# bottom3 = df_comp_all.tail(3)

# colt1, colt2 = st.columns(2)
# colt1.subheader("Top 3")
# colt1.dataframe(top3, hide_index=True)

# colt2.subheader("Bottom 3")
# colt2.dataframe(bottom3, hide_index=True)

# # ============================================
# # SECTION 2 : Comparaisons et évolution
# # ============================================

# st.header("📈 Comparaisons et évolutions")

# # ---- Evolution par niveau ----
# st.subheader("Évolution par niveau")
# mat_choice = st.pills("Matière à afficher", ["Les deux"] + sorted(df["Matière"].unique()), selection_mode="single")

# if mat_choice == "Les deux":
#     df_evol = df_filtre
# else:
#     df_evol = df_filtre[df_filtre["Matière"] == mat_choice]

# df_evol_niv = df_evol.groupby(["Niveau", "Matière"], as_index=False)["Valeur"].mean()
# fig_evol = px.line(df_evol_niv, x="Niveau", y="Valeur", color="Matière", markers=True)
# st.plotly_chart(fig_evol, use_container_width=True)

# # ---- Corrélation compétences ----
# st.subheader("Corrélation entre compétences (moyenne / écart-type)")

# df_corr = (
#     df_filtre.groupby("Compétence", as_index=False)
#     .agg(
#         Moyenne=("Valeur", "mean"),
#         Ecart_type=("Valeur", "std"),
#         Niveaux=("Niveau", lambda x: ", ".join(sorted(set(x))))
#     )
# )
# fig_corr = px.scatter(
#     df_corr,
#     x="Moyenne",
#     y="Ecart_type",
#     hover_data=["Compétence", "Niveaux"],
#     color="Moyenne",
#     color_continuous_scale="RdYlGn",
# )
# st.plotly_chart(fig_corr, use_container_width=True)
# st.caption("Les compétences avec faible moyenne et fort écart-type sont prioritaires pour progresser.")

# # ---- Ecart par réseau (violin) ----
# st.subheader("Écart par réseau")
# fig_violin = px.violin(df_filtre, x="Réseau", y="Valeur", color="Matière", box=True, points="all")
# st.plotly_chart(fig_violin, use_container_width=True)

# # ============================================
# # SECTION 3 : Effet Homologation
# # ============================================

# st.header("🏛️ Effet de l’homologation")

# # ---- Comparaison par matière ----
# df_homo = df_filtre.groupby(["Matière", "Homologué"], as_index=False)["Valeur"].mean()
# fig_homo = px.bar(
#     df_homo,
#     x="Matière",
#     y="Valeur",
#     color="Homologué",
#     barmode="group",
#     text_auto=".2f",
#     title="Moyenne selon homologation"
# )
# st.plotly_chart(fig_homo, use_container_width=True)

# # ---- % d’établissements homologués dans top 10 compétences ----
# top10 = df_filtre.groupby("Compétence")["Valeur"].mean().nlargest(10).index
# pct_homologues = df_filtre[df_filtre["Compétence"].isin(top10)]["Homologué"].eq("oui").mean()
# st.metric("Taux d’homologation dans le top 10 des compétences les mieux maîtrisées", f"{pct_homologues*100:.1f}%")

# # ============================================
# # BONUS : Indice d’équité intra-réseau
# # ============================================

# st.header("⚖️ Indice d’équité intra-réseau")

# df_equite = (
#     df_filtre.groupby("Réseau", as_index=False)
#     .agg(
#         Moyenne=("Valeur", "mean"),
#         Ecart_type=("Valeur", "std"),
#     )
# )
# df_equite["Indice_equité"] = 1 - (df_equite["Ecart_type"] / df_equite["Moyenne"])

# fig_equite = px.bar(df_equite, x="Réseau", y="Indice_equité", title="Indice d’équité intra-réseau")
# st.plotly_chart(fig_equite, use_container_width=True)
