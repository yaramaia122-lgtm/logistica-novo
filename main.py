import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import requests

st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #002D5E !important; }
    div[data-testid="stForm"] { background-color: #002D5E !important; border: none !important; }
    label { color: #FFFFFF !important; font-weight: 700; }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; color: #002D5E !important; border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 800 !important; border-radius: 10px !important; height: 48px !important;
    }
</style>
""", unsafe_allow_html=True)

# 👤 USUÁRIOS REGISTRADOS DIRETO NO APP (Não precisa mais de arquivo no GitHub!)
USUARIOS_REGISTRADOS = {
    "admin": "aura123",
    "yara": "aura2026"
}

if 'logado' not in st.session_state: 
    st.session_state['logado'] = False

if not st.session_state['logado']:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        try:
            url_logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
            st.image(requests.get(url_logo).content, width=280)
        except:
            st.markdown("<h1 style='color:white; text-align:center;'>AURA APOENA</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing:3px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                # Validação direta e instantânea na memória do App
                if u in USUARIOS_REGISTRADOS and USUARIOS_REGISTRADOS[u] == p:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.switch_page("pages/1_📅_Agenda.py")
                else:
                    st.error("Usuário ou Senha incorretos.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 LIMPAR MEMÓRIA CACHE"):
            st.cache_data.clear()
            st.success("Memória limpa!")
else:
    st.switch_page("pages/1_📅_Agenda.py")
