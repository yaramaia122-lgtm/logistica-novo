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

# 🌟 LISTA DE CENTROS DE CUSTO CORPORATIVOS (DEFINIDA GLOBALMENTE PARA EVITAR ERROS)
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
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))

# Limpeza e padronização das colunas
df_v.columns = df_v.columns.str.strip().str.lower()
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

# 3. ABAS DO PAINEL
tab1, tab2 = st.tabs(["Registro Completo de Custos", "Gestão Corporativa de Usuários"])

with tab1:
    st.markdown('<div class="section-header">Inserir ou Alterar Registro Operacional</div>', unsafe_allow_html=True)

    lista_opcoes = ["➕ CRIAR NOVO REGISTRO"]
    for i, row in df_v.iterrows():
        pass_name = str(row.get('passageiro', 'Sem Nome'))
        date_val = str(row.get('data', ''))
        lista_opcoes.append(f"{i} - {pass_name} ({date_val})")

    registro_sel = st.selectbox("🔎 Selecione um registro para ALTERAR ou deixe na primeira opção para CRIAR NOVO:", options=lista_opcoes)

    # Inicialização padrão das variáveis do formulário
    idx_edit = None
    def_pass = ""
    def_cc = "Selecione..."
    def_mot = ""
    def_data = datetime.now().date()
    def_traj = "Pontes e Lacerda x Cuiabá"
    def_status = "Confirmado"
    def_hora = ""
    def_hosp = 0.0
    def_trans = 0.0
    def_aereo = 0.0
    def_outros = 0.0

    # Puxa os dados da linha se for uma alteração/edição
    if registro_sel != "➕ CRIAR NOVO REGISTRO":
        idx_edit = int(registro_sel.split(" - ")[0])
        row_edit = df_v.loc[idx_edit]
        
        def_pass = str(row_edit.get('passageiro', ''))
        def_mot = str(row_edit.get('motorista', ''))
        
        def_cc = str(row_edit.get('centro_custo', 'Selecione...')).strip()
        if def_cc not in lista_centros_custo: 
            def_cc = "Selecione..."
        
        try:
            def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%d/%m/%Y').date()
        except:
            try:
                def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%Y-%m-%d').date()
            except:
                def_data = datetime.now().date()
                
        t_val = str(row_edit.get('trajeto', 'Pontes e Lacerda x Cuiabá')).strip().lower()
        if "cuiaba x pontes e lacerda" in t_val or "cuiabá x pontes e lacerda" in t_val: 
            def_traj = "Cuiabá x Pontes e Lacerda"
        elif "outros" in t_val: 
            def_traj = "Outros Trajetos / Viagem Especial"
        else: 
            def_traj = "Pontes e Lacerda x Cuiabá"

        def_status = str(row_edit.get('status', 'Confirmado')).strip()
        if def_status not in ["Confirmado", "Cancelado", "Ocultado"]: 
            def_status = "Confirmado"

        def_hora = str(row_edit.get('horario', str(row_edit.get('hora_saida', ''))))
        if def_hora == "nan" or def_hora == "None": 
            def_hora = ""
        
        def safe_float(val):
            try: return float(val)
            except: return 0.0
        
        def_hosp = safe_float(row_edit.get('hotel_v', 0.0))
        def_trans = safe_float(row_edit.get('comb_v', 0.0))
        def_aereo = safe_float(row_edit.get('aereo_v', 0.0))
        def_outros = safe_float(row_edit.get('outros_v', 0.0))

    # Desenho do Formulário na Tela
    col1, col2, col3 = st.columns(3)
    with col1:
        in_pass = st.text_input("Nome do Passageiro", value=def_pass if def
