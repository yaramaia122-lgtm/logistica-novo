import streamlit as st
import pandas as pd
from github import Github, Auth
import io

# Configuração básica e limpa da página
st.set_page_config(page_title="AURA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

# CSS Minimalista - Apenas uma linha para evitar o risco de truncar o arquivo
st.markdown("<style>button[data-testid='sidebar-toggle'], section[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)

if 'logado' not in st.session_state: 
    st.session_state['logado'] = False
if 'user' not in st.session_state: 
    st.session_state['user'] = None

def carregar_usuarios():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo_nome = st.secrets["GITHUB_REPO"]
        rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)
        f = rp.get_contents("usuarios.csv")
        df = pd.read_csv(io.StringIO(f.decoded_content.decode()))
        return df
    except:
        # Banco reserva caso o GitHub falhe
        return pd.DataFrame([{"Usuario": "admin", "Senha": "aura123"}, {"Usuario": "yara", "Senha": "aura2026"}])

df_usuarios = carregar_usuarios()
if df_usuarios is not None and not df_usuarios.empty:
    df_usuarios.columns = df_usuarios.columns.str.strip()

# Interface de Login Direta e Sem Firulas para garantir funcionamento
if not st.session_state['logado']:
    _, col_log, _ = st.columns([1, 1.1, 1])
    with col_log:
        st.markdown("<h2 style='text-align:center;'>AURA APOENA</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center; color:#FF7F50;'>LOGÍSTICA</h4>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("ACESSAR SISTEMA")
            
            if btn_login:
                # Verificação exata batendo maiúsculas e minúsculas
                user_match = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == p)]
                if not user_match.empty:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.switch_page("pages/1_Agenda.py")
                else:
                    st.error("Usuário ou Senha incorretos.")
else:
    st.switch_page("pages/1_Agenda.py")
