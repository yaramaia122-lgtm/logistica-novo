import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.write(f"Usuário ativo: **{st.session_state.get('user', 'Funcionário')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['user'] = None
        st.switch_page("main.py")

# Estilo visual original preservado
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 0px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-family: sans-serif !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    def buscar_coluna_case_insensitive(df, nome_esperado):
        for col in df.columns:
            if str(col).strip().lower() == str(nome_esperado).lower():
                return col
        return None

    col_passageiro = buscar_coluna_case_insensitive(df_v, "passageiro") or "passageiro"
    col_trajeto = buscar_coluna_case_insensitive(df_v, "trajeto") or "trajeto"

    # 🛡️ CORREÇÃO DE ESCOPO: Ajustado 'colunas_desejadas' corretamente para evitar o SyntaxError
    def preparar_tabela_segura(df_origem, colunas_desejadas):
        df_saida = pd.DataFrame()
        for col_alvo in colunas_desejadas:
            col_real = buscar_coluna_case_insensitive(df_origem, col_alvo)
            if col_real and col_real in df_origem.columns:
                df_saida[col_alvo] = df_origem[col_real].fillna("").astype(str).str.strip()
            else:
                df_saida[col_alvo] = ""
        return df_saida

    # Listas com as informações essenciais que o motorista precisa
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "motorista"]
    cols_cp =
