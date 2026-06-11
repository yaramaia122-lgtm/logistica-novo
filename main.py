import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import requests

st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #001F42 0%, #002D5E 100%) !important; }
    div[data-testid="stForm"] { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; padding: 30px !important;
    }
    label { color: #FFFFFF !important; font-weight: 600 !important; }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; color: #002D5E !important; border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #FF7F50 !important; color: #FFFFFF !important;
        font-weight: 700 !important; border-radius: 8px !important; height: 46px !important; width: 100% !important;
    }
    section[data-testid="stSidebar"], button[data-testid="sidebar-toggle"], header, footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user' not in st.session_state: st.session_state['user'] = None

def carregar_usuarios():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo_nome = st.secrets["GITHUB_REPO"]
        rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)
        f = rp.get_contents("usuarios.csv")
        df = pd.read_csv(io.StringIO(f.decoded_content.decode()))
        return df
    except:
        return pd.DataFrame([{"Usuario": "admin", "Senha": "aura123"}, {"Usuario": "yara", "Senha": "aura2026"}])

df_usuarios = carregar_usuarios()
if df_usuarios is not None and not df_usuarios.empty:
    df_usuarios.columns = df_usuarios.columns.str.strip()

if not st.session_state['logado']:
    _, col_log, _ = st.columns([1, 1.1, 1])
    with col_log:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        col_1, col_2, col_3 = st.columns([1, 2, 1])
        with col_2:
            try:
                url_logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
                st.image(requests.get(url_logo).content, use_container_width=True)
            except:
                st.markdown("<h1 style='color:white; text-align:center;'>AURA APOENA</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#FF7F50; text-align:center; letter-spacing:
