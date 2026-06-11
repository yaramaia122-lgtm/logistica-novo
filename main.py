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

# Seu visual original intacto
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
    except Exception:
        return pd.DataFrame([{"Usuario": "admin", "Senha": "aura123"}, {"Usuario": "yara", "Senha": "aura2026"}])

df_usuarios = carregar_usuarios()
if df_usuarios is not None and not df_usuarios.empty:
    df_usuarios.columns = df_usuarios.columns.str.strip()

if not st.session_state['logado']:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            url_logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
            st.image(requests.get(url_logo).content, width=280)
        except Exception:
            st.markdown("<h1 style='color:white; text-align:center;'>AURA APOENA</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing:3px;'>LOGISTICA</h2>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("ACESSAR SISTEMA")
            
            if btn_login:
                user_match = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == p)]
                if not user_match.empty:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.switch_page("pages/1_Agenda.py")
                else:
                    st.error("Usuário ou Senha incorretos.")
else:
    st.switch_page("pages/1_Agenda.py")
