import streamlit as st
from utils.loader import load_data
from utils.auth import authenticate, logout

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLF – Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)




# --- Authentification utilisateur ---
# user = authenticate()

# if st.session_state.get("show_welcome", False):
#     st.success(f"Bienvenue, {user} ! 🎉")
#     st.session_state["show_welcome"] = False

# --- Chargement des données ---
with st.spinner("Chargement des données…"):
    df = load_data("result_id")
    df_coordo = load_data("coordinate_id")

# Sauvegarde en mémoire pour toute la session
st.session_state["df"] = df
st.session_state["df_coordo"] = df_coordo

# --- Navigation multipage ---
pages = [
    st.Page("app_pages/1_vue_reseau.py", title="RÉSEAU", icon=":material/globe:"),
    st.Page("app_pages/2_vue_etablissement.py", title="ÉTABLISSEMENT", icon=":material/school:"),
    st.Page("app_pages/3_exploration_avancee.py", title="EXPLORATION", icon=":material/chat:"),
]

pg = st.navigation(pages, position="top")

# --- Exécuter la page active ---
pg.run()

# --- Déconnexion ---
if st.sidebar.button("Se déconnecter"):
    logout()
