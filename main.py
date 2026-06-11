import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import requests

# Configuração formal e ocultação forçada da barra lateral antes do login
st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

# CSS Avançado para esconder a barra lateral na tela de login e estilizar os campos
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
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="sidebar-toggle"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'trocando_senha' not in st.session_state: st.session_state['trocando_senha'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

def carregar_usuarios():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo_nome = st.secrets["GITHUB_REPO"]
        rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)
        f = rp.get_contents("usuarios.csv")
        df = pd.read_csv(io.StringIO(f.decoded_content.decode()))
        return rp, f, df
    except:
        df_reserva = pd.DataFrame([
            {"Usuario": "admin", "Senha": "aura123", "Trocar_Senha": "Nao"},
            {"Usuario": "yara", "Senha": "aura2026", "Trocar_Senha": "Nao"}
        ])
        return None, None, df_reserva

rp, f_github, df_usuarios = carregar_usuarios()

# Força a padronização das colunas do arquivo de usuários para evitar erros de maiúsculas
if df_usuarios is not None and not df_usuarios.empty:
    df_usuarios.columns = df_usuarios.columns.str.strip()

# TELA 1: FLUXO DE TROCA DE SENHA OBRIGATÓRIA
if st.session_state['trocando_senha']:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br><h2 style='color:white; text-align:center;'>Primeiro Acesso</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:white
