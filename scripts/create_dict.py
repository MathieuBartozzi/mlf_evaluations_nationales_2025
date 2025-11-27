import pandas as pd
import json

# -----------------------------------------------------------
# 1) Charger le fichier CSV
# -----------------------------------------------------------

# Remplace éventuellement le chemin ci-dessous si besoin
df = pd.read_csv("scripts/Feuille_7.csv")

# -----------------------------------------------------------
# 2) Construire le dictionnaire imbriqué
#    Format :
#    niveau → matière → domaine → [liste de compétences]
# -----------------------------------------------------------

dictionnaire = {}

for _, row in df.iterrows():

    niveau = row["niveau"]
    matiere = row["matiere"]
    domaine = row["domaine"]
    competence = row["compétence"]

    (
        dictionnaire
            .setdefault(niveau, {})
            .setdefault(matiere, {})
            .setdefault(domaine, [])
            .append(competence)
    )

# -----------------------------------------------------------
# 3) Exporter vers un fichier JSON
# -----------------------------------------------------------

with open("dictionnaire.json", "w", encoding="utf-8") as f:
    json.dump(dictionnaire, f, ensure_ascii=False, indent=4)

print("Fichier dictionnaire.json généré avec succès.")
