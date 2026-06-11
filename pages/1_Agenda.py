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

# Seu estilo e visual original totalmente preservados
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 0px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-family: sans-serif !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

# Funções Auxiliares de Engenharia de Dados fora do bloco principal
def corrigir_colunas_faltantes(df_alvo, colunas_requisitadas):
    df_temp = df_alvo.copy()
    for col in colunas_requisitadas:
        if col not in df_temp.columns: 
            df_temp[col] = ""
    return df_temp[colunas_requisitadas]

def verificar_colunas_html(df_alvo, colunas):
    df_c = df_alvo.copy()
    for c in colunas:
        if c not in df_c.columns: 
            df_c[c] = ""
    return df_c[colunas]

def criar_tabela_html(titulo, df_origem, colunas):
    html = f"<h3>{titulo}</h3>"
    if df_origem.empty:
        return html + "<p>Nenhuma viagem programada.</p>"
    df_seguro = verificar_colunas_html(df_origem, colunas)
    html += "<table><tr>" + "".join(f"<th>{c}</th>" for c in colunas) + "</tr>"
    for _, row in df_seguro.iterrows():
        html += "<tr>" + "".join(f"<td>{str(row[c]) if pd.notna(row[c]) else ''}</td>" for c in colunas) + "</tr>"
    return html + "</table>"

try:
    tk = st.secrets
