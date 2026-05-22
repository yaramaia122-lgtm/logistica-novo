import streamlit as st
import pandas as pd
from github import Github, Auth
import io

st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #002D5E !important; }
    div[data-testid="stForm"] { background-color: #002D5E !important; border: none !important; }
    label { color: #FFFFFF !important; font-weight: 700; }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 800 !important; border-radius: 10px !important; height: 48px !important;
    }
</style>
""", unsafe_allow_html=True)

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                try:
                    tk = st.secrets["GITHUB_TOKEN"]
                    # ATENÇÃO: Certifique-se de que o nome do repositório abaixo está correto
                    rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])
                    f = rp.get_contents("usuarios.csv")
                    df_u = pd.read_csv(io.StringIO(f.decoded_content.decode()))
                    if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.switch_page("pages/1_📅_Agenda.py")
                    else:
                        st.error("Dados incorretos.")
                except Exception as e:
                    st.error("Erro ao conectar ao banco de usuários.")
else:
    st.switch_page("pages/1_📅_Agenda.py")
