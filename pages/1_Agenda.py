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
</style>
""", unsafe_allow_html=True)

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    
    # Forçar cópia limpa com colunas em minúsculo para evitar qualquer conflito
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    # Garantir strings limpas nas colunas essenciais
    for c in df_v.columns:
        df_v[c] = df_v[c].fillna("").astype(str).str.strip()

    # Injeção direta caso alguma coluna não exista no CSV original
    colunas_motorista = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "motorista"]
    for col in colunas_motorista:
        if col not in df_v.columns:
            df_v[col] = ""

    st.markdown('<div class="agenda-header">PROGRAMAÇÃO DA LOGÍSTICA</div>', unsafe_allow_html=True)

    # Filtragem direta baseada em texto purificado
    trajetos_series = df_v["trajeto"].str.lower()

    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_v[trajetos_series == "pontes e lacerda x cuiabá"]
    st.dataframe(df_pl[colunas_motorista], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_v[trajetos_series == "cuiabá x pontes e lacerda"]
    st.dataframe(df_cp[colunas_motorista], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros = df
