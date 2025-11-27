import streamlit as st
import sys, os

# === Import des configs et fonctions utilitaires ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import *
from fonctions_viz import *
from clustering import *
from fonctions import *




if "rapport_open" not in st.session_state:
    st.session_state["rapport_open"] = False

# ===================================================
# PAGE : Vue par établissement
# ===================================================
st.header("Profil d’un établissement")

# Récupération des données en session
df = st.session_state.get("df")
df_coordo = st.session_state.get("df_coordo")

if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez d’abord la page Home.")
    st.stop()

df["Valeur"] = df["Valeur"] * 100
df["niveau_code"] = df["Niveau"].apply(lambda x: ordre_niveaux.index(x))

df_feat = construire_features(df)
df_feat, df_pca, pca, scaler, kmeans = calculer_clustering(df_feat)


# ---------------------------------------------------
# 1️⃣ Sélecteur d’établissement
# ---------------------------------------------------
ecoles = sorted([str(e) for e in df["Nom_ecole"].dropna().unique()])

col1, col2, col3= st.columns(3)
with col1 :
    ecole_selectionnee = st.selectbox("Choisissez un établissement :", ecoles)
    df_ecole = df[df["Nom_ecole"] == ecole_selectionnee]
    # st.subheader(f"{ecole_selectionnee}")

onglets = st.tabs([
    "Statistiques détaillées",
    "Rapport automatique",
])

with onglets[0]:
# with col2 :
#     st.space("small")
#     with st.popover("**Grille de lecture des indicateurs**") :
#         st.markdown("""
# - Les résultats reflètent **des tendances collectives**, pas des performances individuelles.
# - Les moyennes (générale, français, maths) situent l’établissement **par rapport au réseau**, mais ne décrivent pas l’hétérogénéité des classes.
# - Le graphique radar met en évidence :
#   - les **domaines d’appui** (au-dessus du réseau),
#   - les **domaines à renforcer** (en dessous du réseau),
#   - en tenant compte du fait que certains écarts sont **structurels** dans tout le Réseau mlfmonde.
# - La progression **CP→CM2** indique le niveau de cohérence verticale :
#   - évolution régulière → continuité pédagogique stabilisée,
#   - évolution en dents de scie → variations de cohortes, de pratiques ou d’organisation.
# - Le **profil PCA** (fondamentaux, automatisation, complexité) ne classe pas l’établissement :
#   - il aide à **cibler 2–3 leviers prioritaires** pour le pilotage pédagogique.
# """)






    # ---------------------------------------------------
    # 2️⃣ Carte d’identité de l’établissement
    # ---------------------------------------------------

    # # Récupération des infos administratives
    info_ecole = df_ecole[["Réseau", "Statut", "Homologué"]].drop_duplicates().iloc[0]

    # --- Calculs ---
    moy_gen, delta_gen = get_moyenne_et_delta(df, df_ecole)
    moy_fr, delta_fr = get_moyenne_et_delta(df, df_ecole, "Français")
    moy_math, delta_math = get_moyenne_et_delta(df, df_ecole, "Mathématiques")

    # --- Affichage Streamlit ---
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Moyenne générale",
        f"{moy_gen:.1f} %",
        delta=f"{delta_gen:+.1f} pts",
        border=True
    )
    col2.metric(
        "Français",
        f"{moy_fr:.1f} %",
        delta=f"{delta_fr:+.1f} pts",
        border=True
    )
    col3.metric(
        "Mathématiques",
        f"{moy_math:.1f} %",
        delta=f"{delta_math:+.1f} pts",
        border=True
    )



    with st.container(border=True):
        st.subheader("Positionnement général dans le réseau")
        col1, col2 =st.columns([2,1])
        with col1 :
            plot_radar_domaine(df_ecole, df,ecole_selectionnee,palette)

        with col2 :
            plot_scatter_comparatif(df, ecole_selectionnee,palette)

    # ---------------------------------------------------
    # 4️⃣ Heatmap des compétences par niveau
    # ---------------------------------------------------

    with st.container(border=True):
        st.subheader("Progression des apprentissages de CP à CM2")
        col1, col2 =st.columns([2,1])
        with col1 :
            plot_heatmap_competences(df_ecole,ordre_niveaux)
        with col2:
            plot_line_chart(df_ecole, palette, ordre_niveaux)


    # --- Chargement du cluster de l'établissement ---
    cluster_id = int(df_feat.loc[ecole_selectionnee, "cluster"])
    profil = cluster_id + 1

    with st.container(border=True):

        st.subheader("Résultat du profilage")

        col_gauche, col_droite = st.columns([1,1.4])

        # ---------------------------
        # ➤ COLONNE GAUCHE : Profil + axes
        # ---------------------------
        with col_gauche:

            st.markdown(f"Le profil de **{ecole_selectionnee}** est le **profil {profil}**")

            pc1 = df_pca.loc[df_pca["Nom_ecole"] == ecole_selectionnee, "PC1"].values[0]
            pc2 = df_pca.loc[df_pca["Nom_ecole"] == ecole_selectionnee, "PC2"].values[0]
            pc3 = df_pca.loc[df_pca["Nom_ecole"] == ecole_selectionnee, "PC3"].values[0]

            # Affichage des axes
            a1, a2, a3 = st.columns(3)
            a1.metric("Axe 1 – Fondamentaux", f"{pc1:.2f}")
            a2.metric("Axe 2 – Automatisation", f"{pc2:.2f}")
            a3.metric("Axe 3 – Complexité", f"{pc3:.2f}")

            st.caption("Les axes PCA sont centrés sur le réseau : **0 = moyenne**, valeurs positives = **au-dessus**, valeurs négatives = **en-dessous**. Plus l’écart à 0 est fort, plus la position est marquée.")

            # Recommandations en fonction du profil
            st.markdown(get_recommandations_profil(profil))

        # ---------------------------
        # ➤ COLONNE DROITE : Figure PCA 3D
        # ---------------------------
        with col_droite:
            plot_pca_3d(df_pca, ecole_selectionnee, palette)

with onglets[1]:
# st.divider()

    # st.markdown("#### 📄 Génération de rapport d'analyse")
    st.markdown("""
    Une IA peut générer automatiquement un rapport détaillé sur les résultats de votre établissement aux évaluations nationales.
    Vous y trouverez les tendances marquantes, les points forts et les pistes d’amélioration, tout en suggérant des actions de formation pour les enseignants.
    """)

    # --- Gestion du changement d'établissement ---
    # Si on change d'école dans le sélecteur plus haut, on veut effacer l'ancien rapport
    if "last_ecole" not in st.session_state:
        st.session_state["last_ecole"] = ecole_selectionnee

    if st.session_state["last_ecole"] != ecole_selectionnee:
        # On vide le rapport et le PDF si l'école change
        if "rapport_genere" in st.session_state:
            del st.session_state["rapport_genere"]
        if "pdf_ready" in st.session_state:
            del st.session_state["pdf_ready"]
        st.session_state["last_ecole"] = ecole_selectionnee


    # --- Zone de texte pour le contexte local ---
    with st.container(border=True):
        st.write("**Optionnel** : l'IA peut prendre en compte d'autres éléments, notamment de contexte, que vous jugez utiles d'ajouter aux résultats. Deux moyens sont possibles :")

        input1, input2 = st.columns(2)

        with input1:
            contexte_local = st.text_area(
                "Vous pouvez ajouter des informations spécifiques sur l'établissement :",
                placeholder="Exemples :\n"
                            "- Nos élèves sont majoritairement bilingues...\n"
                            "- Notre équipe enseignante est majoritairement composée d’enseignants en contrat local...",
                height=200
            )

        with input2:
            # Upload d'un fichier PDF en complément du contexte local
            pdf_uploaded = st.file_uploader(
                "Vous pouvez téléverser un document complémentaire, 3 pages maximum :",
                type=["pdf"]
            )

            pdf_text = ""
            if pdf_uploaded is not None:
                # Assurez-vous que la fonction extract_text_from_pdf est bien importée ou définie
                pdf_text = extract_text_from_pdf(pdf_uploaded)
                st.success(f"📎 Fichier ajouté : {pdf_uploaded.name}")


    # ---------------------------------------------------
    # ACTION : GÉNÉRATION DU RAPPORT
    # ---------------------------------------------------
    if st.button("⚙️ Générer le rapport", type='primary'):
        with st.spinner("🚧 Votre rapport est en cours de création. Merci de patienter un instant ⏳..."):
            # On refiltre pour être sûr d'avoir les bonnes données
            df_ecole = df[df["Nom_ecole"] == ecole_selectionnee]

            rapport, erreur = generer_rapport_etablissement(
                df,
                ecole_selectionnee,
                contexte_local,
                pdf_text,
            )

            if erreur:
                st.error(erreur)
            else:
                # === SAUVEGARDE EN SESSION ===
                st.session_state["rapport_genere"] = rapport

                # On efface un éventuel vieux PDF pour forcer sa régénération avec le nouveau rapport
                if "pdf_ready" in st.session_state:
                    del st.session_state["pdf_ready"]

                # On recharge la page pour que le bloc d'affichage ci-dessous prenne le relais
                st.rerun()


    # ---------------------------------------------------
    # AFFICHAGE DU RAPPORT (S'il existe en mémoire)
    # ---------------------------------------------------
    if "rapport_genere" in st.session_state:

        rapport_actuel = st.session_state["rapport_genere"]

        st.success("C'est prêt 😊 !")
        st.caption("""
        Ce rapport a été généré automatiquement par une intelligence artificielle
        et doit être interprété avec prudence. Il s’agit d’une analyse basée
        sur les données fournies ; toute décision doit être complétée par une
        réflexion pédagogique et des échanges avec les équipes enseignantes."""
        )


        with st.expander("📄 Découvrir le rapport"):
                st.write(rapport_actuel)

                st.divider()
                _, col2,col3,_ = st.columns(4)
                nom_base = f"Rapport_{ecole_selectionnee.replace(' ', '_')}"


                with col2:
                    st.download_button(
                        label="PDF",
                        data=convert_to_pdf_data(rapport_actuel, ecole_selectionnee),
                        file_name=f"{nom_base}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        icon=":material/download:"
                    )

                # -- BOUTON WORD --
                with col3:

                    st.download_button(
                        label="Word",
                        data=convert_to_word_data(rapport_actuel, ecole_selectionnee),
                        file_name=f"{nom_base}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary", # Couleur différente pour distinguer
                        use_container_width=True,
                        icon=":material/download:"
                    )
