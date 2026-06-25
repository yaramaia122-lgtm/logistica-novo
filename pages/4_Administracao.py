import streamlit as st
import pandas as pd
from github import Github, Auth
import ioimport streamlit as st
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

    # 🌟 A MÁGICA ACONTECE AQUI: SELETOR PARA SABER SE É NOVO OU EDIÇÃO
    lista_opcoes = ["➕ CRIAR NOVO REGISTRO"]
    for i, row in df_v.iterrows():
        pass_name = str(row.get('passageiro', 'Sem Nome'))
        date_val = str(row.get('data', ''))
        lista_opcoes.append(f"{i} - {pass_name} ({date_val})")

    registro_sel = st.selectbox("Selecione um registro para ALTERAR ou deixe na primeira opção para CRIAR NOVO:", options=lista_opcoes)

    # Variáveis padrão (limpas)
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

    # Se selecionou um registro existente, carrega os dados dele!
    if registro_sel != "➕ CRIAR NOVO REGISTRO":
        idx_edit = int(registro_sel.split(" - ")[0]) # Pega o ID da linha selecionada
        row_edit = df_v.loc[idx_edit]
        
        def_pass = str(row_edit.get('passageiro', ''))
        def_mot = str(row_edit.get('motorista', ''))
        
        # Tratamento seguro para resgatar a data
        try:
            def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%d/%m/%Y').date()
        except:
            try:
                def_data = datetime.strptime(str(row_edit.get('data', '')).split(" ")[0], '%Y-%m-%d').date()
            except:
                def_data = datetime.now().date()
                
        t_val = str(row_edit.get('trajeto', 'Pontes e Lacerda x Cuiabá')).strip().lower()
        if t_val == "cuiaba x pontes e lacerda" or t_val == "cuiabá x pontes e lacerda": def_traj = "Cuiabá x Pontes e Lacerda"
        elif "outros" in t_val: def_
from datetime import datetime

# 1. VERIFICAÇÃO DE LOGIN DE USUÁRIO
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Administração - AURA LOGISTICS", layout="wide")

# 🎨 ESTILIZAÇÃO CORPORATIVA E CORES OFICIAIS (SEM EMOJIS)
st.markdown("""<style>
    .stApp { background-color: #F8FAFC !important; }
    .main-title { color: #002D5E !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
    .subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }
    .section-header { background-color: #002D5E !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 10px; margin-bottom: 15px; }
    .subsection-header { color: #002D5E !important; font-weight: bold; font-size: 12pt; margin-top: 15px; margin-bottom: 10px; border-left: 4px solid #FF7F50; padding-left: 8px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Painel Administrativo de Logística</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Gerenciamento centralizado de registros, trajetos, controle financeiro e credenciais de acesso</div>', unsafe_allow_html=True)

# 2. CONEXÃO SEGURA COM O REPOSITÓRIO GITHUB
tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

# 3. CRIAÇÃO DAS GUIAS CORPORATIVAS
aba_custos, aba_usuarios = st.tabs(["Registro Completo de Custos", "Gestão Corporativa de Usuários"])

# =========================================================================
# ABA 1: REGISTRO COMPLETO DE CUSTOS
# =========================================================================
with aba_custos:
    f_file = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(f_file.decoded_content.decode()))

    # Força a coluna data a ser interpretada estritamente como texto formatado para não sumir com as barras
    if "data" in df_v.columns:
        df_v["data"] = df_v["data"].astype(str).str.strip()

    st.markdown('<div class="section-header">Inserir ou Alterar Registro Operacional</div>', unsafe_allow_html=True)

    col_p, col_m, col_d = st.columns(3)
    p_nome = col_p.text_input("Nome do Passageiro")
    m_nome = col_m.selectbox("Motorista Designado", ["Ilson", "Particular", "Outro Profissional"])
    d_viagem = col_d.date_input("Data da Viagem", datetime.now())

    col_t, col_s, col_h = st.columns(3)
    t_escolha = col_t.selectbox("Trajeto Selecionado", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outras Rotas"])
    s_escolha = col_s.selectbox("Status Operacional", ["Confirmado", "Cancelado", "Ocultado"])
    h_saida = col_h.text_input("Horário de Saída (HH:MM)")

    st.markdown('<div class="subsection-header">Apropriação de Custos (R$)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    v_hotel = c1.text_input("Hospedagem", "0.00")
    v_comb = c2.text_input("Transfer / Combustível", "0.00")
    v_aereo = c3.text_input("Passagem Aérea", "0.00")
    v_outros = c4.text_input("Outras Despesas", "0.00")

    if st.button("Gravar Alterações na Base de Dados", width='stretch'):
        if not p_nome.strip():
            st.error("Erro: O preenchimento do nome do passageiro é obrigatório para prosseguir.")
        else:
            try:
                v_total = float(v_hotel) + float(v_comb) + float(v_aereo) + float(v_outros)
                
                novo_reg = {
                    "passageiro": p_nome.strip(), "motorista": m_nome, "data": d_viagem.strftime('%d/%m/%Y'),
                    "hora_saida": h_saida.strip(), "trajeto": t_escolha, "status": s_escolha,
                    "centro_custo": "210301 - Moagem", "hotel_v": v_hotel, "comb_v": v_comb,
                    "aereo_v": v_aereo, "outros_v": v_outros, "total": f"{v_total:.2f}", "voo": ""
                }
                
                df_v = pd.concat([df_v, pd.DataFrame([novo_reg])], ignore_index=True)
                rp.update_file("dados_logistica.csv", "Logistics Base Auto-Update via Admin", df_v.to_csv(index=False), f_file.sha)
                st.success("Registro operacional persistido com sucesso na base de dados."); st.rerun()
            except ValueError:
                st.error("Erro: Certifique-se de que todos os valores informados nos campos de custos são numéricos.")

    st.markdown("---")
    st.markdown('<div class="section-header">Base de Dados Completa (Modo de Exibição e Auditoria)</div>', unsafe_allow_html=True)
    cfg_tabela = {"data": st.column_config.TextColumn("Data", required=True)}
    df_v_editado = st.data_editor(df_v, column_config=cfg_tabela, hide_index=True, width='stretch', key="editor_admin_v_final")

    if st.button("Salvar Modificações Diretas da Tabela", width='content'):
        rp.update_file("dados_logistica.csv", "Tabela Manual Update", df_v_editado.to_csv(index=False), rp.get_contents("dados_logistica.csv").sha)
        st.success("Modificações salvas diretamente no arquivo base."); st.rerun()

# =========================================================================
# ABA 2: GESTÃO CORPORATIVA DE USUÁRIOS
# =========================================================================
with aba_usuarios:
    st.markdown('<div class="section-header">Controle de Usuários e Permissões do Sistema</div>', unsafe_allow_html=True)
    
    f_user = rp.get_contents("usuarios.csv")
    df_u = pd.read_csv(io.StringIO(f_user.decoded_content.decode()))
    
    col_u1, col_u2, col_u3 = st.columns(3)
    novo_usuario = col_u1.text_input("Nome de Usuário (Login)")
    nova_senha = col_u2.text_input("Senha de Acesso", type="password")
    novo_perfil = col_u3.selectbox("Perfil de Acesso", ["admin", "usuario"])
    
    if st.button("Cadastrar Novo Usuário Corporativo", width='content'):
        if not novo_usuario.strip() or not nova_senha.strip():
            st.error("Erro: Usuário e Senha devem ser preenchidos obrigatoriamente.")
        elif novo_usuario.strip() in df_u['usuario'].astype(str).values:
            st.error("Erro: Este nome de usuário já está cadastrado no sistema.")
        else:
            novo_usr_df = pd.DataFrame([{"usuario": novo_usuario.strip(), "senha": nova_senha.strip(), "perfil": novo_perfil}])
            df_u = pd.concat([df_u, novo_usr_df], ignore_index=True)
            rp.update_file("usuarios.csv", "Add user via admin", df_u.to_csv(index=False), f_user.sha)
            st.success(f"Usuário '{novo_usuario}' registrado com sucesso!"); st.rerun()
            
    st.markdown("---")
    st.markdown('<div class="subsection-header">Usuários Ativos no Sistema</div>', unsafe_allow_html=True)
    df_u_editado = st.data_editor(df_u, hide_index=True, width='stretch', key="editor_usuarios_v1")
    
    if st.button("Salvar Alterações na Lista de Usuários", width='content'):
        rp.update_file("usuarios.csv", "Users Manual Update", df_u_editado.to_csv(index=False), rp.get_contents("usuarios.csv").sha)
        st.success("Lista de credenciais atualizada."); st.rerun()
