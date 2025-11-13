import plotly.express as px
# --- Palette globale utilisée dans toute l'app ---

T10 = px.colors.qualitative.T10
# palette = {
#     "etab":T10[1],
#     # "oui": T10[2],
#     "Français":T10[3],
#     "Mathématiques":T10[4],
#     "profil_1": T10[5],
#     "profil_2": T10[6],
#     "profil_3": T10[7],
#     "profil_4": T10[8],
#     "réseau":T10[9],

# }

palette = {
    "etab":T10[2],
    # "oui": T10[2],
    "Français":T10[4],
    "Mathématiques":T10[5],
    "profil_0": T10[6],
    "profil_1": T10[1],
    "profil_2": T10[0],
    "profil_3": T10[3],
    "réseau":T10[9],

}


ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]

CLUSTER_COLORS = {
    0: palette["profil_0"],
    1: palette["profil_1"],
    2: palette["profil_2"],
    3: palette["profil_3"],
}
