import plotly.express as px
# --- Palette globale utilisée dans toute l'app ---

G10 = px.colors.qualitative.G10
palette = {
    "Français":G10[0],
    "Mathématiques":G10[1],
    "Moyenne réseau":G10[2],
    "oui": G10[3],
    "non": G10[4],  #
}

# --- Palette de couleurs partagée ---

ordre_niveaux = ["CP", "CE1", "CE2", "CM1", "CM2"]
