import plotly.express as px
# --- Palette globale utilisée dans toute l'app ---

T10 = px.colors.qualitative.T10
palette = {
    "Français":T10[3],
    "Mathématiques":T10[4],
    "Moyenne réseau":T10[2],
    "oui": T10[3],
    "non": T10[4],  #
}


ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]
