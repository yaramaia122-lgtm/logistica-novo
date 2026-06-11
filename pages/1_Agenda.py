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

# Seu estilo visual original da página preservado integralmente
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 0px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-family: sans-serif !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

def corrigir_colunas_faltantes(df_alvo, colunas_requisitadas):
    df_temp = df_alvo.copy()
    for col in colunas_requisitadas:
        if col not in df_temp.columns: 
            df_temp[col] = ""
    return df_temp[colunas_requisitadas]

def gerar_tabela_html(titulo, df_sub, colunas):
    txt = "<h3>" + str(titulo) + "</h3>"
    if df_sub.empty:
        return txt + "<p style='font-size:12px; color:#666;'>Nenhuma viagem programada para este trecho.</p>"
    df_seguro = df_sub.copy()
    for c in colunas:
        if c not in df_seguro.columns: 
            df_seguro[c] = ""
    txt += "<table><tr>"
    for c in colunas:
        txt += "<th>" + str(c) + "</th>"
    txt += "</tr>"
    for _, row in df_seguro[colunas].iterrows():
        txt += "<tr>"
        for c in colunas:
            val = row[c]
            txt += "<td>" + (str(val) if pd.notna(val) else "") + "</td>"
        txt += "</tr>"
    txt += "</table>"
    return txt

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    # Proteção contra duplicadas de colunas e dados nulos
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    df_v["passageiro"] = df_v["passageiro"].fillna("").astype(str).str.strip() if "passageiro" in df_v.columns else ""
    df_v["trajeto"] = df_v["trajeto"].fillna("").astype(str).str.strip().str.lower() if "trajeto" in df_v.columns else ""

    # Painel de Observações da Tela
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEM
