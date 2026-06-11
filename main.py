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

if df_usuarios is not None and not df_usuarios.empty:
    df_usuarios.columns = df_usuarios.columns.str.strip()

# TELA 1: FLUXO DE TROCA DE SENHA OBRIGATÓRIA
if st.session_state['trocando_senha']:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br><h2 style='color:white; text-align:center;'>Primeiro Acesso</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:white; text-align:center;'>Por políticas de segurança, altere sua senha temporária.</p>", unsafe_allow_html=True)
        
        with st.form("nova_senha_form"):
            nova_senha = st.text_input("Digite sua nova senha definitiva", type="password")
            confirma_senha = st.text_input("Confirme a nova senha", type="password")
            
            if st.form_submit_button("SALVAR NOVA SENHA"):
                if len(nova_senha) < 4:
                    st.error("A senha deve ter pelo menos 4 caracteres.")
                elif nova_senha != confirma_senha:
                    st.error("As senhas informadas não são iguais.")
                else:
                    df_usuarios.loc[df_usuarios['Usuario'] == st.session_state['user_atual'], 'Senha'] = nova_senha
                    df_usuarios.loc[df_usuarios['Usuario'] == st.session_state['user_atual'], 'Trocar_Senha'] = "Nao"
                    if rp and f_github:
                        rp.update_file("usuarios.csv", f"Senha alterada por {st.session_state['user_atual']}", df_usuarios.to_csv(index=False), f_github.sha)
                    st.session_state['logado'] = True
                    st.session_state['user'] = st.session_state['user_atual']
                    st.session_state['trocando_senha'] = False
                    st.success("Senha alterada com sucesso! Redirecionando...")
                    st.switch_page("pages/1_Agenda.py")

# TELA 2: TELA DE LOGIN TRADICIONAL
elif not st.session_state['logado']:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            url_logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
            st.image(requests.get(url_logo).content, width=280)
        except:
            st.markdown("<h1 style='color:white; text-align:center;'>AURA APOENA</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing:3px;'>LOGISTICA</h2>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                user_match = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == p)]
                if not user_match.empty:
                    if user_match.iloc[0]['Trocar_Senha'] == "Sim":
                        st.session_state['user_atual'] = u
                        st.session_state['trocando_senha'] = True
                        st.rerun()
                    else:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.switch_page("pages/1_Agenda.py")
                else:
                    st.error("Usuário ou Senha incorretos.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("LIMPAR MEMÓRIA CACHE"):
            st.cache_data.clear()
            st.success("Memória cache limpa com sucesso.")
else:
    st.switch_page("pages/1_Agenda.py")
