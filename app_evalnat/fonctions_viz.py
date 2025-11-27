import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import *
import numpy as np
import plotly.express as px
import statsmodels.api as sm



# =============================
# Page : vue_reseau.py
# =============================


# moyenne établissement
@st.cache_data
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


@st.cache_data
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
        color_discrete_map=palette,
        hover_data={
        "Critère": False,           # déjà visible dans le titre de facette
        "Critère_valeur": True,     # ex: Maroc, Privé, Oui
        "Matière": True,            # Français / Maths
        "Moyenne": ":.2f",          # valeur brute
        "Valeur_affichée": ":.2f",  # écart ou valeur
    }
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
        height=600,
        legend=dict(
            orientation="h",       # horizontale
            yanchor="bottom",
            y=1.15,                # légèrement au-dessus du graphe
            xanchor="center",
            x=0.5
        ),
    )

   # Supprime les labels/ticks de l’axe X
    fig.for_each_xaxis(lambda ax: ax.update(showticklabels=True, title_text=None, matches=None))


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
        f"{ecole_selectionnee}": palette["etab"],  # couleur de base, on ajustera ensuite
        "Moyenne réseau": palette["réseau"],
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
        height=450,
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
        color_continuous_scale="Viridis",
        text_auto=".1f",
        aspect="auto",
        labels=dict(color="Score moyen (%)")
    )

    fig.update_layout(height=500, margin=dict(l=40, r=40, t=20, b=40),xaxis_title=None,yaxis_title=None )
    st.plotly_chart(fig, use_container_width=True)



def plot_scatter_comparatif(df, ecole_selectionnee,palette):
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
        color_discrete_sequence=[palette["réseau"]],
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
            marker=dict(size=14, color=palette["etab"], line=dict(width=2, color="white"), symbol="diamond"),
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

# --------------------------------------------
# Pie chart distribution des clusters
# --------------------------------------------

def plot_pie_clusters(df_feat):
    cluster_counts = df_feat["cluster"].value_counts().sort_index()

    fig = px.pie(
        names=[f"Profil {i+1}" for i in cluster_counts.index],
        values=cluster_counts.values,
        hole=0.4,
        color=[str(i) for i in cluster_counts.index],
        color_discrete_map={
            str(k): v for k, v in CLUSTER_COLORS.items()
        }

    )
    fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=40, b=40),
            legend=dict(
                orientation="h",      # horizontal
                yanchor="bottom",
                y=-0.2,               # sous le graphique
                xanchor="center",
                x=0.5,
            )
        )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------
# PCA 3D avec point de l'établissement surligné
# --------------------------------------------

def plot_pca_3d(df_pca, ecole_selectionnee,palette):
    df_pca = df_pca.copy()
    df_pca["cluster_str"] = df_pca["cluster"].astype(str)

    fig = px.scatter_3d(
        df_pca,
        x="PC1", y="PC2", z="PC3",
        color="cluster_str",
        hover_name="Nom_ecole",
        opacity=0.8,
        color_discrete_map={
            str(k): v for k, v in CLUSTER_COLORS.items()
        }
    )

    # mise en avant établissement
    df_sel = df_pca[df_pca["Nom_ecole"] == ecole_selectionnee]
    if not df_sel.empty:
        fig.add_trace(go.Scatter3d(
            x=df_sel["PC1"], y=df_sel["PC2"], z=df_sel["PC3"],
            mode="markers+text",
            text=[ecole_selectionnee],
            textposition="top center",
            marker=dict(size=14, color=palette['etab'], line=dict(width=3, color="white"),opacity=1, symbol="diamond"),
            name="Établissement sélectionné",

        ))

    fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(showlegend=False)
    fig.update_layout(scene=dict(
    xaxis_title="1 – Fondamentaux",
    yaxis_title="2 – Automatisation",
    zaxis_title="3 – Complexité",
))
    fig.update_layout(
    scene_camera=dict(
        eye=dict(x=0.7, y=0.7, z=0.8),
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0)
    ))

    st.plotly_chart(fig, use_container_width=True)


def get_recommandations_profil(profil):
    recommandations = {
        1: """
**Recommandations – Profil 1**

- Renforcer le calcul mental structuré quotidien
- Consolider les techniques opératoires
- Introduire plus de tâches numériques répétées
- Utiliser des rituels courts d’automatisation
- Introduire davantage de tâches numériques répétées et ritualisées
- Utiliser des rituels courts d’automatisation (5–7 min)
- S’appuyer sur leurs forces en compréhension pour aborder la résolution de problèmes (verbalisation, reformulation)
- Articuler compréhension ↔ nombre : petits problèmes contextualisés pour automatiser les faits numériques
""",

        2: """
**Recommandations – Profil 2**
- Harmoniser les progressions CP–CM2
- Structurer un référentiel de compétences d’école
- Organiser des conseils de cycle ciblés
- Mettre en place des pratiques pédagogiques communes
- Prioriser les fondamentaux en CP–CE1 : langage oral, décodage, numération
- Renforcer la cohérence interclasses via des outils partagés (fiches méthodes, traces écrites types)
""",

        3: """
**Recommandations – Profil 3**

- Identifier 2–3 fragilités précises pour cibler les actions d’amélioration
- Valoriser et diffuser les pratiques efficaces existantes
- Introduire des défis cognitifs pour maintenir une dynamique de progression
- Développer la métacognition (explicitation des stratégies)
- Travailler la cohérence verticale : aligner certains points clés des progressions
- Renforcer la liaison entre compréhension et résolution de problèmes (transfert de stratégies)
""",

        4: """
**Recommandations – Profil 4**

- Travail intensif et structuré de la compréhension
- Renforcer les langages et le vocabulaire (rituels lexicaux, catégorisation)
- Problèmes verbalisés : expliciter la démarche, reformuler, questionner
- Ateliers de raisonnement et d’inférences
- Développer des stratégies de lecture explicites : repérage d’informations, segmentation, liens logiques
- Mobiliser leurs compétences mathématiques pour soutenir la compréhension(lecture comme résolution de problème : étapes, indices, preuves)
"""
    }
    return recommandations.get(profil, "Profil inconnu")


def color_dot(color):
    return f'<span style="color:{color};font-size:2em;">●</span>'

def square(color):
    return f'<span style="background:{color}; width:12px; height:12px; display:inline-block;"></span>'




# --------------------------------------------
# page 3
# --------------------------------------------

def vue_top_bottom_matiere(df, matiere, n=5):
    key_segment = f"seg_{matiere}"   # 🔥 clé unique

    options_map = {
        "+": ":material/add:  + maîtrisées",
        "-": ":material/remove:  - maîtrisées",
    }

    choix = st.segmented_control(
        f"{matiere}",
        options=options_map.keys(),
        format_func=lambda o: options_map[o],
        selection_mode="single",
        default="+",
        key=key_segment,   # 🔑 clé unique obligatoire
    )

    df_mat = df[df["Matière"] == matiere]
    df_mean = df_mat.groupby("Compétence")["Valeur"].mean().reset_index()

    top_n = df_mean.sort_values("Valeur", ascending=False).head(n)
    bottom_n = df_mean.sort_values("Valeur", ascending=True).head(n)

    if choix == "+":
        st.dataframe(top_n, use_container_width=True)
    else:
        st.dataframe(bottom_n, use_container_width=True)


def plot_distribution_competences(df, nbins=30):
    """
    Histogramme des scores des COMPÉTENCES.
    1 point = 1 compétence (moyenne réseau).
    """

    df_comp = (
        df.groupby(["Matière", "Compétence"])["Valeur"]
        .mean()
        .reset_index()
    )

    fig = px.histogram(
        df_comp,
        x="Valeur",
        color="Matière",
        nbins=nbins,
        barmode="overlay",
        color_discrete_map=palette,

    )

    fig.update_layout(
        bargap=0.05,
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="Niveau de maîtrise (%)",
        yaxis_title="Nombre de compétences",
    )

    st.plotly_chart(fig, use_container_width=True)



def plot_swarm_competences(df, palette, seuil_std=12, height=480):

    df = df.copy()

    # 1. Compétences discriminantes
    std_by_comp = df.groupby("Compétence")["Valeur"].std()
    compet_discri = std_by_comp[std_by_comp >= seuil_std].index
    df["is_discri"] = df["Compétence"].isin(compet_discri)

    # 2. Ordre stable des compétences
    compet_order = sorted(df["Compétence"].unique())
    df["Comp_idx"] = df["Compétence"].apply(lambda c: compet_order.index(c))

    # 3. Couleur finale
    df["color_display"] = df.apply(
        lambda r: "red" if r["is_discri"] else palette[r["Matière"]],
        axis=1
    )

    # 4. Jitter pour simuler le swarm
    jitter = np.random.uniform(-0.05, 0.05, size=len(df))
    df["x_jitter"] = df["Comp_idx"] + jitter

    fig = go.Figure()

    # ========= TRACE SWARM UNIQUE =========
    fig.add_trace(go.Scatter(
        x=df["x_jitter"],
        y=df["Valeur"],
        mode="markers",
        marker=dict(
            color=df["color_display"],
            size=6,
            opacity=0.6
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Matière : %{customdata[1]}<br>" +
            "Valeur : %{y:.1f}%<br>" +
            "<extra></extra>"
        ),
        customdata=np.stack([df["Compétence"], df["Matière"]], axis=1),
        showlegend=False
    ))

    # ========= LÉGENDE MANUELLE =========
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(size=10, color=palette["Français"]),
        name="Français"
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(size=10, color=palette["Mathématiques"]),
        name="Mathématiques"
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(size=10, color="red"),
        name="Compétences discriminantes"
    ))

    # ========= LAYOUT =========
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="center",
            x=0.5,
            font=dict(size=13)
        ),

        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(compet_order))),
            ticktext=compet_order,
            showticklabels=False
        ),
        yaxis=dict(title="% de maîtrise")
    )

    return fig


def list_competences_discriminantes(df, seuil_std=12):
    """
    Retourne deux dataframes :
    - compétences discriminantes en Français
    - compétences discriminantes en Mathématiques
    Basé sur l'écart-type (dispersion) et le seuil fourni.
    """

    df = df.copy()

    # 1. Calcul de l'écart-type par compétence × matière
    df_var = df.groupby(["Matière", "Compétence"])["Valeur"].std().reset_index()
    df_var = df_var.rename(columns={"Valeur": "ecart_type"})

    # 2. Filtrer selon seuil
    df_discri = df_var[df_var["ecart_type"] >= seuil_std]

    # 3. Séparer par matière
    df_fr = df_discri[df_discri["Matière"] == "Français"].sort_values("ecart_type", ascending=False)
    df_math = df_discri[df_discri["Matière"] == "Mathématiques"].sort_values("ecart_type", ascending=False)

    return df_fr, df_math



def plot_scatter_dispersion(df, palette, seuil_std=12, height=520):

    df = df.copy()

    # ===============================
    # 1. Agrégation compétence × matière
    # ===============================
    df_disp = df.groupby(["Compétence", "Matière"])["Valeur"].agg(["mean", "std"]).reset_index()

    # ===============================
    # 2. Marquage des compétences discriminantes
    # ===============================
    df_disp["is_discri"] = df_disp["std"] >= seuil_std

    # Couleur : rouge si discriminante, sinon palette matière
    df_disp["color_display"] = df_disp.apply(
        lambda r: ("#d62728" if r["is_discri"] else palette[r["Matière"]]),
        axis=1
    )


    # ===============================
    # 3. Scatter principal
    # ===============================
    fig = px.scatter(
        df_disp,
        x="mean",
        y="std",
        color="color_display",
        hover_data=["Compétence"],
        labels={"mean": "Moyenne (%)", "std": "Dispersion (écart-type)"},
        color_discrete_map="identity"
    )

    # Taille unique des points
    fig.update_traces(marker=dict(size=10, line=dict(width=0)))

    # ===============================
    # 4. Zones pédagogiques
    # ===============================
    ymax = df_disp["std"].max() + 2

    # fig.add_shape(type="rect", x0=0, x1=50, y0=0, y1=ymax,
    #               fillcolor="rgba(255,0,0,0.06)", line_width=0)

    # fig.add_shape(type="rect", x0=85, x1=100, y0=0, y1=ymax,
    #               fillcolor="rgba(0,150,255,0.08)", line_width=0)

    fig.add_shape(type="rect", x0=50, x1=85, y0=seuil_std, y1=ymax,
                  fillcolor="rgba(255,0,0,0.06)", line_width=0)

    # ===============================
    # 5. Lignes de référence
    # ===============================
    fig.add_vline(x=50, line_dash="dot", opacity=0.4)
    fig.add_vline(x=85, line_dash="dot", opacity=0.4)
    fig.add_hline(y=seuil_std, line_dash="dot", line_color="orange", opacity=0.4)

    # ===============================
    # 6. Annotations
    # ===============================
    fig.add_annotation(x=45, y=ymax - 0.5, text="Difficiles", showarrow=False,
                       font=dict(size=12))
    fig.add_annotation(x=92, y=ymax - 0.5, text="Stables", showarrow=False,
                       font=dict(size=12))
    fig.add_annotation(x=67, y=ymax - 0.5, text="À surveiller", showarrow=False,
                       font=dict(size=12))

    # ===============================
    # 7. Courbe LOWESS
    # ===============================
    lowess = sm.nonparametric.lowess(df_disp["std"], df_disp["mean"], frac=0.2)
    fig.add_trace(go.Scatter(
        x=lowess[:, 0],
        y=lowess[:, 1],
        mode="lines",
        line=dict(color="lightgray", width=1, dash="dot"),
        name="Tendance"
    ))

    # ===============================
    # 8. Nouvelle légende simplifiée
    # ===============================
    legend_items = [
        go.Scatter(x=[None], y=[None], mode='markers',
                   marker=dict(size=10, color=palette["Français"]),
                   name="Français"),
        go.Scatter(x=[None], y=[None], mode='markers',
                   marker=dict(size=10, color=palette["Mathématiques"]),
                   name="Mathématiques"),
        go.Scatter(x=[None], y=[None], mode='markers',
                   marker=dict(size=10, color="#d62728"),
                   name="Compétences discriminantes"),
    ]
    for item in legend_items:
        fig.add_trace(item)

    fig.update_layout(
        legend=dict(
            orientation="h",
            y=1.18,
            x=0.5,
            xanchor="center",
            font=dict(size=14)
        ),
        xaxis=dict(range=[40, 100]),   # <--- commence à 0 !
        height=height,
        margin=dict(l=20, r=20, t=80, b=20),
    )

    return fig




def afficher_top_bottom_evolutions(df):
    """Affiche Top 3 et Bottom 3 selon l'évolution moyenne (slope),
    avec choix de la matière (Français / Maths), uniquement par Compétence."""

    colonnes_requises = {'Matière', 'Compétence', 'slope'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir les colonnes : Matière, Compétence, slope.")
        return

    # Choix matière
    matiere = st.segmented_control(
        "Choisissez la matière :",
        ["Français", "Mathématiques"],
        selection_mode="single",
        default="Français"
    )

    # Filtre matière
    df_filtre = df[df["Matière"] == matiere]

    if df_filtre.empty:
        st.warning(f"Aucune donnée disponible pour {matiere}.")
        return

    # Groupby compétence
    grouped = (
        df_filtre
        .groupby("Compétence", as_index=False)["slope"]
        .mean()
        .round(3)
        .sort_values(by="slope", ascending=False)
    )
    grouped = grouped.rename(columns={"slope": "Progression", "spearman": "Régularité"})


    # Top 3
    top3 = grouped.head(3).reset_index(drop=True)

    # Bottom 3
    bottom3 = (
        grouped.tail(3)
        .sort_values(by="Progression", ascending=True)
        .reset_index(drop=True)
    )

    # Affichage

    st.write("**Top 3 progressions (compétence)**")
    st.dataframe(top3, use_container_width=True)

    st.write("**Bottom 3 régressions (compétence)**")
    st.dataframe(bottom3, use_container_width=True)


# def afficher_bar_domaine_prog(df):
#     """Affiche un barplot des progressions moyennes par domaine (colonne slope)."""

#     colonnes_requises = {"Domaine", "slope"}
#     if not colonnes_requises.issubset(df.columns):
#         st.error("Le DataFrame doit contenir les colonnes : Domaine, slope.")
#         return

#     df_dom = (
#         df.groupby("Domaine")["slope"]
#         .mean()
#         .reset_index()
#         .sort_values("slope")
#     )

#     df_dom["Couleur"] = df_dom["slope"].apply(
#         lambda x: "Progression" if x >= 0 else "Régression"
#     )

#     fig = px.bar(
#         df_dom,
#         x="Domaine",
#         y="slope",
#         color="Couleur",
#         color_discrete_map=palette,
#         height=550
#     )

#     # ---- AXES SIMPLIFIÉS ----
#     fig.update_xaxes(
#         title=None,       # ❌ enlève "Domaine"
#         tickangle=35      # Rotation lisible
#     )

#     fig.update_yaxes(
#         title="Pente (slope)"   # ✔️ remet slope à gauche
#     )

#     # ---- LÉGENDE ----
#     fig.update_layout(
#         margin=dict(l=0, r=0, t=40, b=0),
#         legend_title=None,  # ❌ enlève "Couleur"
#         legend=dict(
#             orientation="h",
#             y=1.15,
#             x=0.5,
#             xanchor="center",
#             font=dict(size=14)
#         ),
#         template="simple_white"  # ✔️ style propre et sobre
#     )
#     fig.add_hline(y=0, line_color="black", line_width=1)

#     st.plotly_chart(fig, use_container_width=True)



# def plot_regularity_vs_slope(df, palette):

#     df = df.copy()
#     df["spearman"] = df["spearman"].abs()

#     # FIGURE DE BASE
#     fig = px.scatter(
#         df,
#         x="slope",
#         y="spearman",
#         color="Domaine",
#         # hover_data=["Compétence"],
#         color_discrete_map=palette,
#         height=500
#     )

#     # limites pour les zones
#     x_min = df["slope"].min()
#     x_max = df["slope"].max()
#     y_min = df["spearman"].min()
#     y_max = df["spearman"].max()

#     # === QUADRANTS ===
#     fig.add_shape(
#         type="rect",
#         # x0=0, x1=x_max, y0=0, y1=y_max,
#         fillcolor="rgba(0, 180, 0, 0.1)",  # vert doux
#         line_width=0,
#         layer="below"
#     )  # +pente / +spearman

#     fig.add_shape(
#         type="rect",
#         x0=0, x1=x_max, y0=y_min, y1=0,
#         fillcolor="rgba(0, 120, 255, 0.1)",  # bleu clair
#         line_width=0,
#         layer="below"
#     )  # +pente / -spearman

#     fig.add_shape(
#         type="rect",
#         x0=x_min, x1=0, y0=0, y1=y_max,
#         fillcolor="rgba(255, 200, 0, 0.15)",  # jaune
#         line_width=0,
#         layer="below"
#     )  # -pente / +spearman

#     fig.add_shape(
#         type="rect",
#         x0=x_min, x1=0, y0=y_min, y1=0,
#         fillcolor="rgba(255, 0, 0, 0.1)",  # rouge léger
#         line_width=0,
#         layer="below"
#     )  # -pente / -spearman

#     # LIGNES CENTRALES
#     fig.add_hline(y=0, line_color="black", line_width=1)
#     fig.add_vline(x=0, line_color="black", line_width=1)

#     fig.update_layout(
#         legend=dict(
#             orientation="h",
#             y=1.18,
#             x=0.5,
#             xanchor="center",
#             font=dict(size=14)
#         ),
#         margin=dict(l=0, r=0, t=40, b=0),
#         xaxis_title="Pente (slope)",
#         yaxis_title="Corrélation de Spearman",
#         legend_title="",
#         template="simple_white"

#     )
#     fig.update_traces(marker=dict(size=10, line=dict(width=0)))

#     st.plotly_chart(fig, use_container_width=True)


def afficher_courbes_en_grille(df_reseau, df_evol, nb_niveaux=3, n_cols=4):
    comps = df_evol[df_evol["nb_niveaux"] == nb_niveaux]["Compétence"].unique()

    # 👉 Si aucune compétence pour ce nombre de niveaux, afficher un message clair
    if len(comps) == 0:
        st.info(
            f"Aucune compétence n’a été évaluée sur {nb_niveaux} niveaux. "
            "Essayez un autre nombre de niveaux pour visualiser des progressions."
        )
        return  # On sort proprement de la fonction

    n = len(comps)
    # n_rows = math.ceil(n / n_cols)

    index = 0
    # for r in range(n_rows):
    cols = st.columns(n_cols)

    for col in cols:
        if index >= n:
            break

        c = comps[index]
        df_c = df_reseau[df_reseau["Compétence"] == c].sort_values("niveau_code")

        fig_c = px.line(
            df_c,
            x="Niveau",
            y="Valeur",
            markers=True,
            height=300
        )

        fig_c.update_layout(
           title=dict(
               text=c,
               font=dict(size=10),
               x=0
               )
           )
        fig_c.update_yaxes(title="")
        fig_c.update_xaxes(title="")
        # fig_c.update_xaxes(title_font=dict(size=11))

        col.plotly_chart(fig_c, use_container_width=True)
        index += 1



# def afficher_bars_progression_regularity(df, palette):
#     """
#     Affiche un bar chart comparatif normalisé (entre -1 et +1)
#     montrant la progression (pente) et la régularité (|Spearman|)
#     par domaine.

#     Le df doit contenir les colonnes :
#         - 'Domaine'
#         - 'slope'
#         - 'spearman'
#     """

#     colonnes_requises = {"Domaine", "slope", "spearman"}
#     if not colonnes_requises.issubset(df.columns):
#         st.error("Le DataFrame doit contenir : Domaine, slope, spearman.")
#         return

#     df_plot = df.copy()
#     df_plot["spearman_abs"] = df_plot["spearman"].abs()

#     # --- Normalisation min–max sécurisée ---
#     for col in ["slope", "spearman_abs"]:
#         cmin = df_plot[col].min()
#         cmax = df_plot[col].max()
#         if cmax - cmin == 0:
#             df_plot[col + "_norm"] = 0
#         else:
#             df_plot[col + "_norm"] = (df_plot[col] - cmin) / (cmax - cmin) * 2 - 1

#     # --- Préparation long format pour plotly ---
#     df_long = df_plot.melt(
#         id_vars=["Domaine"],
#         value_vars=["slope_norm", "spearman_abs_norm"],
#         var_name="Indicateur",
#         value_name="Valeur"
#     )

#     # --- Bar chart ---
#     fig = px.bar(
#         df_long,
#         x="Valeur",
#         y="Domaine",
#         color="Indicateur",
#         barmode="group",
#         orientation="h",
#         color_discrete_map=palette
#     )

#     fig.update_layout(
#         # title="Progression et régularité  par domaine",
#         template="simple_white",
#         height=500,
#         legend=dict(
#             orientation="h",
#             y=-0.15,
#             x=0.5,
#             xanchor="center"
#         ),
#         xaxis=dict(title=""),
#         yaxis=dict(title="")
#     )

#     st.plotly_chart(fig, use_container_width=True)

def afficher_bars_progression_regularity(df, palette):
    """
    Affiche un bar chart comparatif normalisé :
        - pente ∈ [-1, +1]
        - régularité (|Spearman|) ∈ [0, +1]
    par domaine.
    """

    colonnes_requises = {"Domaine", "slope", "spearman"}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir : Domaine, slope, spearman.")
        return

    df_plot = df.copy()
    df_plot["spearman_abs"] = df_plot["spearman"].abs()

    # --- Normalisation pente en [-1, 1] ---
    cmin = df_plot["slope"].min()
    cmax = df_plot["slope"].max()
    if cmax - cmin == 0:
        df_plot["slope_norm"] = 0
    else:
        df_plot["slope_norm"] = (df_plot["slope"] - cmin) / (cmax - cmin) * 2 - 1

    # --- Normalisation spearman_abs en [0, 1] ---
    smin = df_plot["spearman_abs"].min()
    smax = df_plot["spearman_abs"].max()
    if smax - smin == 0:
        df_plot["spearman_abs_norm"] = 0
    else:
        df_plot["spearman_abs_norm"] = (df_plot["spearman_abs"] - smin) / (smax - smin)

    # --- Passage en long format ---
    df_long = df_plot.melt(
        id_vars=["Domaine"],
        value_vars=["slope_norm", "spearman_abs_norm"],
        var_name="Indicateur",
        value_name="Valeur"
    )
    #Renomage personnalisé des indicateurs pour la légende
    df_long["Indicateur"] = df_long["Indicateur"].replace({
        "slope_norm": "Progression",
        "spearman_abs_norm": "Régularité"
    })


    # --- Bar chart ---
    fig = px.bar(
        df_long,
        x="Valeur",
        y="Domaine",
        color="Indicateur",
        barmode="group",
        orientation="h",
        color_discrete_map=palette
    )

    fig.update_layout(
        template="simple_white",
        height=500,
        legend=dict(
            title=None,
            orientation="h",
            y=-0.15,
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(title=""),
        yaxis=dict(title="")
    )

    st.plotly_chart(fig, use_container_width=True)
