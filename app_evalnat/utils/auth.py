import streamlit as st

def authenticate():
    """
    Vérifie l'identité de l'utilisateur via un formulaire simple.
    Utilise st.secrets["auth"]["users"] et st.secrets["auth"]["password"].
    Retourne le prénom/nom "friendly" si connexion réussie.
    """

    # Si déjà connecté, on ne redemande pas
    if st.session_state.get("auth_ok"):
        return st.session_state["username_friendly"]

    st.header("🔒 Connexion")

    # Formulaire de connexion
    with st.form("login_form"):
        email = st.text_input("Adresse e-mail")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

    if not submitted:
        st.stop()  # on arrête le script tant que l'utilisateur n'a pas cliqué

    # Récupération des infos depuis .streamlit/secrets.toml
    allowed_users = st.secrets["auth"]["users"]     # dictionnaire {email: "Nom affiché"}
    shared_password = st.secrets["auth"]["password"]

    # Vérification de l’email
    if email not in allowed_users:
        st.error("Adresse e-mail non autorisée.")
        st.stop()

    # Vérification du mot de passe
    if password != shared_password:
        st.error("Mot de passe incorrect.")
        st.stop()

    # ✅ Authentification réussie → on sauvegarde en session
    st.session_state["auth_ok"] = True
    st.session_state["user_email"] = email
    st.session_state["username_friendly"] = allowed_users[email]
    st.session_state["show_welcome"] = True  # drapeau pour message de bienvenue

    return allowed_users[email]


def logout():
    """
    Déconnecte l'utilisateur en réinitialisant l'état de session.
    """
    for key in ["auth_ok", "user_email", "username_friendly"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Vous avez été déconnecté.")
    st.stop()
