import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import requests

# Configuração formal da página e ocultação da barra lateral antes do login
st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

# CSS Otimizado para a Interface de Login (Sem risco de quebra de string)
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #001F42 0%, #002D5E 100%) !important; }
    div[data-testid="stForm"] { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; padding: 30px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    label { color: #FFFFFF !important; font-weight: 600 !important; font-size: 14px !important; }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; color: #002D5E !important; 
        border: none !important; border-radius: 8px !important; height: 42px !important;
    }
    .stButton>button {
        background-color: #FF7F50 !important; color: #FFFFFF !important;
        font-weight: 700 !important; border: none !important; border-radius: 8px !important; 
        height: 46px !important; width: 100% !important; font-size: 16px !important;
        letter-spacing: 1px; box-shadow: 0 4px 12px rgba(255, 127, 80, 0.3) !important;
    }
    section[data-testid="stSidebar"], button[data-testid="sidebar-toggle"], header, footer { display: none !important; }
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
if df_usuarios is not None and not df_usuarios.empty:
    df_usuarios.columns = df_usuarios.columns.str.strip()

# TELA 1: FLUXO DE TROCA DE SENHA OBRIGATÓRIA
if st.session_state['trocando_senha']:
    _, col_log, _ = st.columns([1, 1.1, 1])
    with col_log:
        st.markdown("<br><br><h2 style='color:white; text-align:center;'>Primeiro Acesso</h2>", unsafe_allow_html=True)
        with st.form("nova_senha_form"):
            nova_senha = st.text_input("Nova Senha Definitiva", type="password")
            confirma_senha = st.text_input("Confirme a Nova Senha", type="password")
            if st.form_submit_button("SALVAR NOVA
