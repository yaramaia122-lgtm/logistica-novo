import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import requests

# Configuração original da página
st.set_page_config(
    page_title="AURA APOENA LOGISTICS", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Seu visual original com linhas quebradas para não truncar no GitHub
st.markdown("""
<style>
    .stApp { 
        background-color: #002D5E !important; 
    }
    div[data-testid="stForm"] { 
        background-color: #002D5E !important; 
        border: none !important; 
    }
    label { 
        color: #FFFFFF !important; 
        font-weight: 700; 
    }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; 
        color: #002D5E !important; 
        border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #FFFFFF !important; 
        color: #002D5E !important;
        font-weight: 800 !important; 
        border-radius: 10px !important; 
        height: 48px !important;
    }
    section[data-testid="stSidebar"] { 
        display: none !important; 
    }
    button[data-testid="sidebar-toggle"] { 
        display: none !important; 
    }
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
    except
