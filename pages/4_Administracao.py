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

    registro_sel = st.selectbox("Selecione um registro para ALTERAR ou deixe na primeira opção para CRIAR NOVO:", options=lista_opcoes)

    idx_edit = None
    def_pass = ""
    def_mot = ""
    def_data = datetime.now().date()
    def_traj = "Pontes e Lacerda x Cuiabá"
    def_status = "Confirmado"
    def_hora = ""
    def_hosp = 0.0
    def_trans = 0.0
    def_aereo = 0.0
    def_outros = 0.0

    if registro_sel != "➕ CRIAR NOVO REGISTRO":
        idx_edit = int(registro_sel.split(" - ")[0]) 
        row_edit = df_v.loc[idx_edit]
        
        def_pass = str(row_edit.get('passageiro', ''))
        def_mot = str(row_edit.get('motorista', ''))
        
        try:
            def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%d/%m/%Y').date()
        except:
            try:
                def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%Y-%m-%d').date()
            except:
                def_data = datetime.now().date()
                
        t_val = str(row_edit.get('trajeto', 'Pontes e Lacerda x Cuiabá')).strip().lower()
        if t_val == "cuiaba x pontes e lacerda" or t_val == "cuiabá x pontes e lacerda": def_traj = "Cuiabá x Pontes e Lacerda"
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

    col1, col2, col3 = st.columns(3)
    with col1:
        in_pass = st.text_input("Nome do Passageiro", value=def_pass if def_pass != 'nan' else "")
        in_traj = st.selectbox("Trajeto Selecionado", options=["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros Trajetos / Viagem Especial"], index=["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros Trajetos / Viagem Especial"].index(def_traj))
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
                df_novo = pd.DataFrame([nova_linha])
                df_v = pd.concat([df_v, df_novo], ignore_index=True)
                msg_sucesso = "Novo registro criado com sucesso!"
            else:
                for k, v in nova_linha.items():
                    df_v.at[idx_edit, k] = v
                msg_sucesso = "Registro atualizado com sucesso!"

            rp.update_file("dados_logistica.csv", "Admin Painel Update", df_v.to_csv(index=False), f_log.sha)
            st.success(msg_sucesso)
            st.rerun()

    st.markdown('<div class="section-header">Base de Dados Completa (Modo de Exibição e Auditoria)</div>', unsafe_allow_html=True)
    st.dataframe(df_v, use_container_width=True)

with tab2:
    st.info("Área de gestão de usuários em desenvolvimento.")
