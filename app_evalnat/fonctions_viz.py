import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =============================
# Page : vue_reseau.py
# =============================

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
    colonnes_requises = {'Nom_ecole', 'Domaine', 'Compétence', 'Valeur'}
    if not colonnes_requises.issubset(df.columns):
        st.error("Le DataFrame doit contenir les colonnes : Nom_ecole, Domaine, Compétence, Valeur.")
        return

    labels = {"École": "Nom_ecole", "Domaine": "Domaine", "Compétence": "Compétence"}

    choix_label = st.segmented_control(
        "Choisissez le niveau d'analyse :",
        list(labels.keys()),
        selection_mode="single",
        default="École"
    )

    choix = labels[choix_label]

    grouped = df.groupby(choix, as_index=False)["Valeur"].mean().round(2)
    grouped = grouped.sort_values(by="Valeur", ascending=False)
    grouped = grouped.rename(columns={'Nom_ecole': 'École'})

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
