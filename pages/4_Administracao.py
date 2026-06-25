import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime
import string
import random

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
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))
df_v.columns = df_v.columns.str.strip().str.lower()
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

try:
    f_user = rp.get_contents("usuarios.csv")
    df_u = pd.read_csv(io.StringIO(f_user.decoded_content.decode()))
    df_u.columns = df_u.columns.str.strip().str.lower()
except Exception:
    df_base_u = pd.DataFrame([{"usuario": "adm", "senha": "aura123"}])
    df_u = df_base_u.copy()

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
    st.markdown('<div class="section-header">Gestão Corporativa de Usuários do Sistema</div>', unsafe_allow_html=True)
    
    with st.form("form_novo_usuario"):
        st.write("### Cadastrar Novo Usuário Administrativo")
        new_user = st.text_input("Nome de Usuário (Login):").strip()
        
        # Lógica do Gerador Automático
        c_auto, c_manual = st.columns([1, 2])
        with c_auto:
            gerar_auto = st.checkbox("🎲 Gerar senha automaticamente", value=True)
        with c_manual:
            new_pass = st.text_input("Senha de Acesso (Manual):", type="password", disabled=gerar_auto, help="Desmarque a caixa ao lado para digitar uma senha manual.").strip()
            
        btn_user = st.form_submit_button("🔐 Adicionar Novo Usuário")
        
        if btn_user:
            senha_final = new_pass
            
            if gerar_auto:
                caracteres = string.ascii_letters + string.digits + "@#$"
                senha_final = ''.join(random.choice(caracteres) for i in range(8))
                
            if not new_user:
                st.error("Por favor, preencha o nome de usuário.")
            elif not gerar_auto and not senha_final:
                st.error("Por favor, digite uma senha ou marque para gerar automaticamente.")
            elif new_user.lower() in df_u['usuario'].astype(str).str.lower().values:
                st.error("Este usuário já está cadastrado no sistema!")
            else:
                new_row = pd.DataFrame([{"usuario": new_user, "senha": senha_final}])
                df_u_final = pd.concat([df_u, new_row], ignore_index=True)
                
                f_user_current = rp.get_contents("usuarios.csv")
                rp.update_file("usuarios.csv", "Novo usuario adicionado via painel", df_u_final.to_csv(index=False), f_user_current.sha)
                
                # Atualiza em memória para a tabela exibir sem precisar atualizar a página inteira (assim a senha não some)
                df_u = df_u_final 
                
                if gerar_auto:
                    st.success(f"✅ Usuário **{new_user}** criado com sucesso!")
                    st.info(f"🔑 **Senha gerada:** `{senha_final}`  \n*(Copie esta senha agora, pois ela não será exibida novamente!)*")
                else:
                    st.success(f"✅ Usuário '{new_user}' cadastrado com sucesso!")
                
    st.write("### Usuários com Acesso Ativo")
    st.dataframe(df_u, use_container_width=True)
    
    usuarios_deletar = [u for u in df_u['usuario'].astype(str).tolist() if u.lower() != 'adm']
    if usuarios_deletar:
        st.write("### Remover Credencial de Acesso")
        user_to_del = st.selectbox("Selecione um usuário para excluir do sistema:", options=[""] + usuarios_deletar)
        if st.button("❌ Excluir Credencial Selecionada"):
            if user_to_del:
                df_u_final = df_u[df_u['usuario'].astype(str) != user_to_del]
                f_user_current = rp.get_contents("usuarios.csv")
                rp.update_file("usuarios.csv", "Usuario removido via painel", df_u_final.to_csv(index=False), f_user_current.sha)
                st.success(f"Usuário '{user_to_del}' removido com sucesso!")
                st.rerun()
