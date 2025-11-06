

"""
convert_evaluations.py
----------------------
Ce script lit un Google Sheet contenant plusieurs onglets d'évaluations nationales
(CP, CE1, CE2, CM1, CM2), nettoie les données et crée un fichier longitudinal CSV.
La configuration (URL du Google Sheet) est stockée dans un fichier .env.
"""

import pandas as pd
import re
import sys
import os
from dotenv import load_dotenv
from domaines_dict import DOMAINES_DICT


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Charger les variables d'environnement depuis .env
load_dotenv()

GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
if not GOOGLE_SHEET_URL:
    sys.exit("❌ Erreur : la variable GOOGLE_SHEET_URL est absente du fichier .env")

NIVEAUX = ['CP', 'CE1', 'CE2', 'CM1', 'CM2']

# ---------------------------------------------------------------------------
# FONCTIONS
# ---------------------------------------------------------------------------

def load_google_sheet(sheet_url):
    """Charge le fichier Google Sheet en tant que ExcelFile via l’URL publique."""
    try:
        sheet_id = re.findall(r"/d/([a-zA-Z0-9-_]+)", sheet_url)[0]
        xls = pd.ExcelFile(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx")
        return xls
    except Exception as e:
        sys.exit(f"❌ Erreur lors du chargement du Google Sheet : {e}")


def get_matiere_et_domaine(competence, domaines_dict):
    """Associe une compétence à une matière et un domaine à partir d’un dictionnaire."""
    for matiere, domaines in domaines_dict.items():
        for domaine, mots in domaines.items():
            if any(mot.lower() in str(competence).lower() for mot in mots):
                return matiere, domaine
    return None, None


def clean_percentage(val):
    """
    Convertit proprement une valeur de type '85%', '0.85', 85, etc.
    en float arrondi sur 2 décimales (ex: 0.85).
    """
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.strip().replace(",", ".").replace(" ", "")
        if val.endswith("%"):
            try:
                return round(float(val.replace("%", "")) / 100, 2)
            except ValueError:
                return None
        try:
            return round(float(val), 2)
        except ValueError:
            return None
    try:
        val = float(val)
        if val > 1:
            return round(val / 100, 2)
        return round(val, 2)
    except Exception:
        return None


def process_sheet(sheet_name, xls, domaines_dict):
    """Nettoie et transforme un onglet spécifique en format long."""
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    # On garde les lignes à partir de la 4e (index 3)
    df = df.iloc[3:].reset_index(drop=True)

    # Première ligne = entêtes
    df.columns = df.iloc[0]
    df = df.drop(0).reset_index(drop=True)

    # Colonnes fixes établissement
    meta_cols = ['Nom_ecole', 'Pays', 'Ville', 'Statut', 'Réseau', 'Homologué']

    # Vérification des colonnes de métadonnées
    expected_meta = set(meta_cols)
    actual_meta = set(df.columns) & expected_meta
    missing_meta = expected_meta - actual_meta
    if missing_meta:
        print(f"⚠️ [{sheet_name}] Colonnes manquantes : {', '.join(missing_meta)}")

    # Suppression des colonnes inutiles
    df = df.loc[:, ~df.columns.str.contains("Moyenne", na=False)]
    df = df.dropna(axis=1, how="all")

    # Colonnes de compétences
    comp_cols = [c for c in df.columns if c not in meta_cols]

    # Passage au format long
    df_long = df.melt(
        id_vars=meta_cols,
        value_vars=comp_cols,
        var_name='Compétence',
        value_name='Valeur'
    )

    # Nettoyage du pourcentage
    df_long["Valeur"] = df_long["Valeur"].apply(clean_percentage)

    # Ajout du niveau
    df_long['Niveau'] = sheet_name

    # Attribution matière / domaine
    df_long[['Matière', 'Domaine']] = df_long['Compétence'].apply(
        lambda c: pd.Series(get_matiere_et_domaine(c, domaines_dict))
    )

    # Vérifications de cohérence
    anomalies = df_long[df_long['Valeur'].isna()]
    if len(anomalies) > 0:
        print(f"⚠️ [{sheet_name}] {len(anomalies)} valeurs manquantes dans les compétences.")

    return df_long


def build_longitudinal(sheet_url):
    """Assemble tous les onglets du Google Sheet en un seul fichier CSV."""
    xls = load_google_sheet(sheet_url)
    all_data = []

    print("🚀 Début du traitement...\n")

    for niveau in NIVEAUX:
        if niveau in xls.sheet_names:
            print(f"→ Traitement de l’onglet {niveau}")
            df_long = process_sheet(niveau, xls, DOMAINES_DICT.get(niveau, DOMAINES_DICT))
            all_data.append(df_long)
        else:
            print(f"⚠️ Onglet {niveau} manquant")

    if not all_data:
        sys.exit("❌ Aucun onglet valide trouvé. Vérifie les noms : CP, CE1, CE2, CM1, CM2.")

    final_df = pd.concat(all_data, ignore_index=True)

    # Rapport de contrôle des domaines inconnus
    inconnus = final_df[final_df['Matière'].isna()]
    if len(inconnus) > 0:
        print(f"⚠️ {len(inconnus)} compétences non classées dans un domaine.")
        print(inconnus['Compétence'].unique())
        inconnus[['Niveau', 'Compétence']].drop_duplicates().to_csv("competences_inconnues.csv", index=False)
        print("💾 Liste enregistrée dans competences_inconnues.csv")

    # Réorganisation des colonnes pour faciliter les tris et groupby
    colonnes_finales = [
        "Niveau",
        "Matière",
        "Domaine",
        "Compétence",
        "Nom_ecole",
        "Pays",
        "Ville",
        "Réseau",
        "Statut",
        "Homologué",
        "Valeur"
    ]

    colonnes_finales = [col for col in colonnes_finales if col in final_df.columns]
    final_df = final_df[colonnes_finales]

    # 📂 Dossier de sortie existant
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))  # remonte d’un cran
    data_dir = os.path.join(parent_dir, "data")

    # Chemin du fichier de sortie
    save_path = os.path.join(data_dir, "résultats_longitudinaux.csv")

    # Sauvegarde du CSV
    final_df.to_csv(save_path, index=False, encoding="utf-8-sig")

    print(f"\n✅ Fichier longitudinal créé : {save_path}")
    print(f"📊 Total de lignes : {len(final_df)}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build_longitudinal(GOOGLE_SHEET_URL)
