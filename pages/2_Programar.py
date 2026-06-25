import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime
import zoneinfo

# 1. VERIFICAÇÃO DE LOGIN
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Programar Transporte - AURA LOGISTICS", layout="wide")

# CSS DA TELA
css_tela = "<style>"
css_tela += ".stApp { background-color: #F8FAFC !important; }"
css_tela += ".main-title { color: #1b294b !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }"
css_tela += ".subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }"
css_tela += ".section-header { background-color: #1b294b !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }"
css_tela += "</style>"
st.markdown(css_tela, unsafe_allow_html=True)

st.markdown('<div class="main-title">Programar Novo Transporte</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Insira os dados da viagem. O sistema definirá o dia da semana automaticamente.</div>', unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
tk = st.secrets["GITHUB_TOKEN"]
repo = st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))

dias_semana_pt = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje = datetime.now(fuso).date()

# 3. FORMULÁRIO DE CADASTRO
st.markdown('<div class="section-header">Informações Gerais e de Faturamento</div>', unsafe_allow_html=True)

col_geral1, col_geral2 = st.columns(2)
with col_geral1:
    passageiro = st.text_input("Nome do Passageiro:", key="prog_passageiro").strip()
    trajeto = st.selectbox("Selecione o Trajeto:", [
        "Pontes e Lacerda x Cuiabá", 
        "Cuiabá x Pontes e Lacerda", 
        "Outros Trajetos / Viagem Especial"
    ])

with col_geral2:
    # 🌟 LISTA SUSPENSA OFICIAL ATUALIZADA COM OS SEUS CENTROS DE CUSTO
    lista_centros_custo = [
        "Selecione...",
        "210301 - Moagem",
        "210403 - Detox",
        "210801 - Laboratório",
        "211002 - Manutenção Mecânica Planta",
        "210405 - Lixiviação / Cianetação",
        "210101 - Administração Planta",
        "211001 - Manutencao Eletrica Planta",
        "211003 - Oficina Manutenção Planta",
        "210201 - Britagem Primária",
        "210604 - Fundição",
        "310101 - Almoxarifado",
        "320401 - Controladoria e Contabilidade",
        "310701 - Serviços Gerais",
        "320601 - Celula de Gestao de Contratos",
        "320101 - Suprimentos",
        "320502 - Tecnologia da Informação",
        "311202 - Care and Maintenance SF",
        "330102 - Apoena Corporativo",
        "311203 - Care and Maintenance PPQ",
        "340103 - Jurídico",
        "310801 - Seguranca Patrimonial",
        "310301 - PCP",
        "320201 - Gerência Geral",
        "310508 - Comunidades",
        "320303 - Trainee",
        "320301 - Recursos Humanos",
        "310902 - Campo",
        "310904 - Exploração EPP",
        "121101 - Geologia Operacional - Mina Ernesto",
        "121102 - Planejamento e Topografia Operacional - Mina Ernes",
        "151101 - Geologia Operacional - Mina Nosde",
        "151103 - Geotecnia - Nosde",
        "210502 - Barragem",
        "151102 - Planejamento e Topografia Operacional - Mina Nosde",
        "310501 - Meio Ambiente",
        "310503 - Segurança do Trabalho",
        "310502 - Saude",
        "150101 - Administração de Mina - Céu Aberto - Nosde",
        "120101 - Administração de Mina - Céu Aberto - Ernesto"
    ]
    centro_custo = st.selectbox("Centro de Custo (Oculto na Agenda):", options=lista_centros_custo, key="prog_cc")
    motorista = st.text_input("Motorista Designado:", key="prog_motorista").strip()

if trajeto == "Pontes e Lacerda x Cuiabá":
    st.markdown('<div class="section-header">Logística: Saída de Pontes e Lacerda para Cuiabá</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        data_ida = st.date_input("Data da Saída:", value=hoje, key="pl_data")
        horario_ida = st.text_input("Horário da Saída (Ex: 06:00):", key="pl_hora")
    with col2:
        saida_loc = st.text_input("Local de Saída/Embarque:", key="pl_sa
