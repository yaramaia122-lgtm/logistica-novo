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

# Inicialização de estados de sessão
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'trocando_senha' not in st.session_state: st.session_state['trocando_senha'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

# Função para carregar usuários do arquivo usuarios.csv no GitHub (para salvar as trocas de senha)
def carregar_usuarios():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo_nome = st.secrets["GITHUB_REPO"]
        rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)
        f = rp.get_contents("usuarios.csv")
        df = pd.read_csv(io.StringIO(f.decoded_content.decode()))
        return rp, f, df
    except:
        # Banco de contingência caso o arquivo não exista ou falhe
        df_reserva = pd.DataFrame([
            {"Usuario": "admin", "Senha": "aura123", "Trocar_Senha": "Nao"},
            {"Usuario": "colaborador", "Senha": "mudar123", "Trocar_Senha": "Sim"}
        ])
        return None, None, df_reserva

rp, f_github, df_usuarios = carregar_usuarios()

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
                    # Atualiza a senha no banco de dados e muda o status de troca para 'Nao'
                    df_usuarios.loc[df_usuarios['Usuario'] == st.session_state['user_atual'], 'Senha'] = nova_senha
                    df_usuarios.loc[df_usuarios['Usuario'] == st.session_state['user_atual'], 'Trocar_Senha'] = "Nao"
                    
                    # Salva direto no GitHub de forma silenciosa
                    if rp and f_github:
                        rp.update_file("usuarios.csv", f"Senha alterada por {st.session_state['user_atual']}", df_usuarios.to_csv(index=False), f_github.sha)
                    
                    st.session_state['logado'] = True
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
                    # Verifica se este usuário precisa trocar a senha obrigatoriamente
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
else:
    st.switch_page("pages/1_Agenda.py")
