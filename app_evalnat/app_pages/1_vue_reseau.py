import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.header("Vue d’ensemble du réseau")

df = st.session_state.get('df')
df_coordo = st.session_state.get('df_coordo')



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
col1.metric("Moyenne générale", f"{moy_globale:.1f} %",border=True)
col2.metric("Mathématiques", f"{moy_maths:.2f}%",border=True)
col3.metric("Français", f"{moy_fr:.2f}%",border=True)


# # ============================================
# # Ligne 2 : Cartographie
# # ============================================

# Moyenne des valeurs par école
df_mean = df.groupby("Nom_ecole", as_index=False)["Valeur"].mean()
# Fusion des moyennes avec les coordonnées géographiques
df_map = pd.merge(
    df_mean,
    df_coordo,
    on="Nom_ecole",
    how="left"
)
df_map = df_map.rename(columns={'Valeur': 'Moyenne'})
df_map["Moyenne"] = df_map["Moyenne"] * 100
df_map["Moyenne etab"] = df_map["Moyenne"].map(lambda x: f"{x:.2f} %")
df_map = df_map.dropna()



fig = px.scatter_mapbox(
    df_map,
    lat="Lat",
    lon="Long",
    size="Moyenne",                  # Taille des points selon la moyenne
    color="Moyenne",                 # Couleur selon la moyenne
    hover_name="Nom_ecole",
    hover_data={"Lat": False, "Long": False, "Moyenne": False,"Moyenne etab": True},
    color_continuous_scale="Viridis",
    zoom=1,
    height=650
)
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_center={"lat": df_map["Lat"].mean(), "lon": df_map["Long"].mean()},
    margin={"r":0, "t":0, "l":0, "b":0}
)
st.plotly_chart(fig, use_container_width=True)



# ============================================
# SECTION 2 : Moyennes par domaine
# ============================================

st.subheader("📊 Moyennes par domaine")

# --- Filtres via st.pills ---
reseaux = sorted(df["Réseau"].dropna().unique())
statuts = sorted(df["Statut"].dropna().unique())
homologations = sorted(df["Homologué"].dropna().unique())

col1, col2, col3 = st.columns(3)
reseau_sel = col1.pills("Réseau", reseaux, selection_mode="multi")
statut_sel = col2.pills("Statut", statuts, selection_mode="multi")
homo_sel = col3.pills("Homologué", homologations, selection_mode="multi")

# --- Application des filtres (directement sur df) ---
mask = pd.Series(True, index=df.index)

if reseau_sel:
    mask &= df["Réseau"].isin(reseau_sel)
if statut_sel:
    mask &= df["Statut"].isin(statut_sel)
if homo_sel:
    mask &= df["Homologué"].isin(homo_sel)

df_filtered = df[mask]

# --- Calcul des moyennes par domaine ---
df_domaine = (
    df_filtered.groupby("Domaine", as_index=False)
    .agg(Moyenne=("Valeur", "mean"))
    .sort_values("Moyenne", ascending=False)
)

# --- Affichage du bar chart ---
if df_domaine.empty:
    st.warning("Aucune donnée ne correspond à cette sélection.")
else:
    fig_bar = px.bar(
        df_domaine,
        x="Moyenne",
        y="Domaine",
        orientation="h",
        color="Moyenne",
        color_continuous_scale="RdYlGn",
        title="Moyenne par domaine"
    )
    fig_bar.update_layout(
        xaxis_title="Moyenne",
        yaxis_title="Domaine",
        height=600,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# colmap, colbar = st.columns([1.2, 1])

# # ---- Carte réseau ----
# df_ecoles = df_filtre.groupby(["Nom de l’école", "Pays", "Ville", "Réseau"], as_index=False).agg(
#     Moyenne=("Valeur", "mean")
# )

# fig_map = px.scatter_geo(
#     df_ecoles,
#     locations="Pays",
#     locationmode="country names",
#     color="Moyenne",
#     hover_name="Nom de l’école",
#     hover_data=["Réseau", "Moyenne"],
#     projection="natural earth",
#     color_continuous_scale="RdYlGn",
# )
# fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
# colmap.plotly_chart(fig_map, use_container_width=True)

# # ---- Domaine choisi ----
# domaine_sel = colbar.pills("Choisir un domaine", df_filtre["Domaine"].unique(), selection_mode="single")
# if domaine_sel:
#     df_dom = df_filtre[df_filtre["Domaine"] == domaine_sel]
#     df_comp = df_dom.groupby(["Compétence", "Matière"], as_index=False)["Valeur"].mean()
#     fig_bar = px.bar(
#         df_comp,
#         x="Valeur",
#         y="Compétence",
#         color="Matière",
#         orientation="h",
#         title=f"Moyenne des compétences ({domaine_sel})",
#     )
#     colbar.plotly_chart(fig_bar, use_container_width=True)

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
