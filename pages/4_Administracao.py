import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

# 1. VERIFICAÇÃO DE LOGIN
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Painel Administrativo - AURA LOGISTICS", layout="wide")

# CSS DA TELA
css_tela = """<style>
.stApp { background-color: #F8FAFC !important; }
.main-title { color: #1b294b !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
.subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }
.section-header { background-color: #1b294b !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }
</style>"""
st.markdown(css_tela, unsafe_allow_html=True)

st.markdown('<div class="main-title">Painel Administrativo de Logística</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Gerenciamento centralizado de registros, trajetos, controle financeiro e credenciais de acesso</div>', unsafe_allow_html=True)

# LISTA DE CENTROS DE CUSTO CORPORATIVOS
lista_centros_custo = [
    "Selecione...", "120101 - Administração de Mina - Céu Aberto - Ernesto", 
    "150101 - Administração de Mina - Céu Aberto - Nosde", "210101 - Administração Planta",
    "210201 - Britagem Primária", "210301 - Moagem", "210403 - Detox", "210405 - Lixiviação / Cianetação", 
    "210502 - Barragem", "210604 - Fundição", "210801 - Laboratório", "211001 - Manutencao Eletrica Planta", 
    "211002 - Manutenção Mecânica Planta", "211003 - Oficina Manutenção Planta", "310101 - Almoxarifado", 
    "310301 - PCP", "310501 - Meio Ambiente", "310502 - Saude", "310503 - Segurança do Trabalho", 
    "310508 - Comunidades", "310701 - Serviços Gerais", "310801 - Seguranca Patrimonial", 
    "311202 - Care and Maintenance SF", "311203 - Care and Maintenance PPQ", "320101 - Suprimentos", 
    "320201 - Gerência Geral", "320301 - Recursos Humanos", "320303 - Trainee", 
    "320401 - Controladoria e Contabilidade", "320502 - Tecnologia da Informação", 
    "320601 - Celula de Gestao de Contratos", "330102 - Apoena Corporativo", "340103 - Jurídico",
    "310902 - Campo", "310904 - Exploração EPP", "121101 - Geologia Operacional - Mina Ernesto",
    "121102 - Planejamento e Topografia Operacional - Mina Ernes", "151101 - Geologia Operacional - Mina Nosde",
    "151103 - Geotecnia - Nosde", "151102 - Planejamento e Topografia Operacional - Mina Nosde"
]

# 2. CONEXÃO GITHUB
tk = st.secrets["GITHUB_TOKEN"]
repo = st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_
