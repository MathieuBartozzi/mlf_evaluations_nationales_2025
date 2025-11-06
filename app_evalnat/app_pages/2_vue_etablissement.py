# pages/1_Overview.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.header("Vue établissement")




df = st.session_state.get('df')
if df is None or df.empty:
    st.warning("Aucune donnée disponible. Ouvrez la page Home")
    st.stop()
