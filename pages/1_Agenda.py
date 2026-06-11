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

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 0px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-family: sans-serif !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

def garantir_colunas_trechos(df_alvo, colunas_requisitadas):
    df_temp = df_alvo.copy()
    for col in colunas_requisitadas:
        if col not in df_temp.columns:
            df_temp[col] = ""
        else:
            df_temp[col] = df_temp[col].fillna("").astype(str).str.strip()
    return df_temp[colunas_requisitadas]

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    df_v["passageiro"] = df_v["passageiro"].fillna("").astype(str).str.strip() if "passageiro" in df_v.columns else ""
    df_v["trajeto"] = df_v["trajeto"].fillna("").astype(str).str.strip().str.lower() if "trajeto" in df_v.columns else ""

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        c_dia.markdown(f"<p style='padding-top:15px; font-weight:bold; color:#333333;'>{row.get('dia', '')}</p>", unsafe_allow_html=True)
        c_data.markdown(f"<p style='padding
