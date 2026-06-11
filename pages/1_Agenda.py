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

# Seu visual original totalmente preservado
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

    # Leitura direta e crua dos arquivos (Sem manipulação prejudicial de colunas)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    # Mapeamento tolerante: buscamos a coluna independentemente de ser "Passageiro" ou "passageiro"
    def buscar_coluna_case_insensitive(df, nome_esperado):
        for col in df.columns:
            if col.strip().lower() == nome_esperado.lower():
                return col
        return None

    col_passageiro = buscar_coluna_case_insensitive(df_v, "passageiro") or "passageiro"
    col_trajeto = buscar_coluna_case_insensitive(df_v, "trajeto") or "trajeto"

    # Criamos uma função de renderização que não deforma o DataFrame original
    def preparar_tabela_segura(df_origem, colunas_desejadas):
        df_saida = pd.DataFrame()
        for col_alvo in colunas_requisitadas:
            col_real = buscar_coluna_case_insensitive(df_origem, col_alvo)
            if col_real and col_real in df_origem.columns:
                df_saida[col_alvo] = df_origem[col_real].fillna("").astype(str).str.strip()
            else:
                df_saida[col_alvo] = ""
        return df_saida

    # Configuração das colunas exatas que o motorista necessita
    colunas_requisitadas = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "motorista"]
    colunas_outros = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    # Render das Observações da Semana
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    col_obs_texto = buscar_coluna_case_insensitive(df_o, "observacao") or "observacao"
    
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        c_dia.markdown(f"<p style='padding-top:15px
