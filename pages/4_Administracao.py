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

# CSS DO ECRÃ
css_tela = """<style>
.stApp { background-color: #F8FAFC !important; }
.main-title { color: #1b294b !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
.subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }
.section-header { background-color: #1b294b !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }
</style>"""
st.markdown(css_tela, unsafe_allow_html=True)

st.markdown('<div class="main-title">Painel Administrativo de Logística</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Gerenciamento centralizado de registos, trajetos, controle financeiro e credenciais de acesso</div>', unsafe_allow_html=True)

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
tab1, tab2 = st.tabs(["Registo Completo de Custos", "Gestão Corporativa de Usuários"])

with tab1:
    st.markdown('<div class="section-header">Inserir ou Alterar Registo Operacional</div>', unsafe_allow_html=True)

    # 🌟 A MÁGICA DA EDIÇÃO: SELETOR DE REGISTOS
    lista_opcoes = ["➕ CRIAR NOVO REGISTO"]
    for i, row in df_v.iterrows():
        pass_name = str(row.get('passageiro', 'Sem Nome'))
        date_val = str(row.get('data', ''))
        lista_opcoes.append(f"{i} - {pass_name} ({date_val})")

    # Esta é a caixa que estava a faltar no seu ecrã!
    registro_sel = st.selectbox("🔎 Selecione um registo para ALTERAR ou deixe na primeira opção para CRIAR NOVO:", options=lista_opcoes)

    # Variáveis Padrão
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

    # Lista Oficial de Centros de Custo
    lista_centros_custo = [
        "Selecione...", "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manutenção Mecânica Planta",
        "210405 - Lixiviação / Cianetação", "210101 - Administração Planta", "211001 - Manutencao Eletrica Planta",
        "211003 - Oficina Manutenção Planta", "210201 - Britagem Primária", "210604 - Fundição",
        "310101 - Almoxarifado", "320401 - Controladoria e Contabilidade", "310701 - Serviços Gerais",
        "320601 - Celula de Gestao de Contratos", "320101 - Suprimentos", "320502 - Tecnologia da Informação",
        "311202 - Care and Maintenance SF", "330102 - Apoena Corporativo", "311203 - Care and Maintenance PPQ",
        "340103 - Jurídico", "310801 - Seguranca Patrimonial", "310301 - PCP", "320201 - Gerência Geral",
        "310508 - Comunidades", "320303 - Trainee", "320301 - Recursos Humanos", "310902 - Campo",
        "310904 - Exploração EPP", "121101 - Geologia Operacional - Mina Ernesto",
        "121102 - Planejamento e Topografia Operacional - Mina Ernes", "151101 - Geologia Operacional - Mina Nosde",
        "151103 - Geotecnia - Nosde", "210502 - Barragem", "151102 - Planejamento e Topografia Operacional - Mina Nosde",
        "310501 - Meio Ambiente", "310503 - Segurança do Trabalho", "310502 - Saude",
        "150101 - Administração de Mina - Céu Aberto - Nosde", "120101 - Administração de Mina - Céu Aberto - Ernesto"
    ]

    # Carrega dados se for Edição
    if registro_sel != "➕ CRIAR NOVO REGISTRO":
        idx_edit = int(registro_sel.split(" - ")[0])
        row_edit = df_v.loc[idx_edit]
        
        def_pass = str(row_edit.get('passageiro', ''))
        def_mot = str(row_edit.get('motorista', ''))
        def_cc = str(row_edit.get('centro_custo', 'Selecione...'))
        if def_cc not in lista_centros_custo: def_cc = "Selecione..."
        
        try:
            def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%d/%m/%Y').date()
        except:
            try:
                def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%Y-%m-%d').date()
            except:
                def_data = datetime.now().date()
                
        t_val = str(row_edit.get('trajeto', 'Pontes e Lacerda x Cuiabá')).strip().lower()
        if "cuiaba x pontes e lacerda" in t_val or "cuiabá x pontes e lacerda" in t_val: def_traj = "Cuiabá x Pontes e Lacerda"
        elif "outros" in t_val: def_traj = "Outros Trajetos / Viagem Especial"
        else: def_traj = "Pontes e Lacerda x Cuiabá"

        def_status = str(row_edit.get('status', 'Confirmado'))
        if def_status not in ["Confirmado", "Cancelado", "Ocultado"]: def_status = "Confirmado"

        def_hora = str(row_edit.get('horario', str(row_edit.get('hora_saida', ''))))
        if def_hora == "nan": def_hora = ""
        
        def safe_float(val):
            try: return float(val)
            except: return 0.0
        
        def_hosp = safe_float(row_edit.get('hotel_v', 0.0))
        def_trans = safe_float(row_edit.get('comb_v', 0.0))
        def_aereo = safe_float(row_edit.get('aereo_v', 0.0))
        def_outros = safe_float(row_edit.get('outros_v', 0.0))

    # Formulário Renderizado
    col1, col2, col3 = st.columns(3)
    with col1:
        in_pass = st.text_input("Nome do Passageiro", value=def_pass if def_pass != 'nan' else "")
        in_traj = st.selectbox("Trajeto Selecionado", options=["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros Trajetos / Viagem Especial"], index=["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros Trajetos / Viagem Especial"].index(def_traj))
        in_cc = st.selectbox("Centro de Custo", options=lista_centros_custo, index=lista_centros_custo.index(def_cc))
    with col2:
        in_mot = st.text_input("Motorista Designado", value=def_mot if def_mot != 'nan' else "")
        in_status = st.selectbox("Status Operacional", options=["Confirmado", "Cancelado", "Ocultado"], index=["Confirmado", "Cancelado", "Ocultado"].index(def_status))
    with col3:
        in_data = st.date_input("Data da Viagem", value=def_data)
        in_hora = st.text_input("Horário de Saída (HH:MM)", value=def_hora if def_hora != 'nan' else "")

    st.markdown("**Apropriação de Custos (R$)**")
    c1, c2, c3, c4 = st.columns(4)
    with c1: in_hosp = st.number_input("Hospedagem", value=float(def_hosp), step=10.0, format="%.2f")
    with c2: in_trans = st.number_input("Transfer / Combustível", value=float(def_trans), step=10.0, format="%.2f")
    with c3: in_aereo = st.number_input("Passagem Aérea", value=float(def_aereo), step=10.0, format="%.2f")
    with c4: in_outros = st.number_input("Outras Despesas", value=float(def_outros), step=10.0, format="%.2f")

    # SALVANDO AS INFORMAÇÕES NO GITHUB
    if st.button("Gravar Alterações na Base de Dados", width='stretch'):
        if not in_pass:
            st.error("O nome do passageiro é obrigatório.")
        else:
            total_custo = in_hosp + in_trans + in_aereo + in_outros
            t_save = in_traj.lower().replace("á", "a")
            if "outros" in t_save: t_save = "outros trajetos / viagem especial"

            nova_linha = {
                "passageiro": in_pass,
                "motorista": in_mot,
                "centro_custo": in_cc if in_cc != "Selecione..." else "",
                "data": in_data.strftime('%d/%m/%Y'),
                "trajeto": t_save,
                "status": in_status,
                "horario": in_hora,
                "hora_saida": in_hora,
                "hotel_v": in_hosp,
                "comb_v": in_trans,
                "aereo_v": in_aereo,
                "outros_v": in_outros,
                "total": total_custo
            }

            if idx_edit is None:
                # É NOVO REGISTRO
                df_novo = pd.DataFrame([nova_linha])
                df_v = pd.concat([df_v, df_novo], ignore_index=True)
                msg_sucesso = "Novo registo criado com sucesso!"
            else:
                # É EDIÇÃO: Atualiza apenas a linha certa!
                for k, v in nova_linha.items():
                    df_v.at[idx_edit, k] = v
                msg_sucesso = "Registo atualizado com sucesso!"

            rp.update_file("dados_logistica.csv", "Admin Painel Update", df_v.to_csv(index=False), f_log.sha)
            st.success(msg_sucesso)
            st.rerun()

    st.markdown('<div class="section-header">Base de Dados Completa (Modo de Exibição e Auditoria)</div>', unsafe_allow_html=True)
    st.dataframe(df_v, use_container_width=True)

with tab2:
    st.info("Área de gestão de usuários em desenvolvimento.")
