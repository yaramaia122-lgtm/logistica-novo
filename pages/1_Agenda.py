import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

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

# Seu visual original intacto
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
</style>
""", unsafe_allow_html=True)

try:
    tk, repo_nome = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)
    
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    # 🛡️ PROTEÇÃO TOTAL CONTRA DUPLICATAS E TRAJETOS NULOS
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    df_v["passageiro"] = df_v["passageiro"].fillna("").astype(str).str.strip() if "passageiro" in df_v.columns else ""
    df_v["trajeto"] = df_v["trajeto"].fillna("").astype(str).str.strip().str.lower() if "trajeto" in df_v.columns else ""

    def renderizar_seguro(df_alvo, colunas):
        df_temp = df_alvo.copy()
        for c in colunas:
            if c not in df_temp.columns: df_temp[c] = ""
        return df_temp[colunas]

    # Bloco de Observações
    dias_sem = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    df_o["observacao"] = df_o["observacao"].fillna("").astype(str) if "observacao" in df_o.columns else ""
    
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for idx, r in df_o.iterrows():
        c_dia, c_data, c_txt = st.columns([1.5, 1, 6.5])
        c_dia.markdown(f"<p style='padding-top:15
