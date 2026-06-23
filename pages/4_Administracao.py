import streamlit as st
import pandas as pd
from github import Github, Auth
import io
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
    .section-header { background-color: #002D5E !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 20px; margin-bottom: 15px; }
    .subsection-header { color: #002D5E !important; font-weight: bold; font-size: 12pt; margin-top: 15px; margin-bottom: 10px; border-left: 4px solid #FF7F50; padding-left: 8px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Painel Administrativo de Logística</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Gerenciamento centralizado de registros, trajetos e controle financeiro operacional</div>', unsafe_allow_html=True)

# 2. CONEXÃO SEGURA COM O REPOSITÓRIO GITHUB
tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_file = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_file.decoded_content.decode()))

# 🛠️ CORREÇÃO CRÍTICA DE FORMATO: Força a coluna data a ser interpretada estritamente como texto formatado
if "data" in df_v.columns:
    df_v["data"] = df_v["data"].astype(str).str.strip()

# 3. FORMULÁRIO ESTRUTURADO DE INCLUSÃO E ALTERAÇÃO DE DADOS
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
                "passageiro": p_nome.strip(), 
                "motorista": m_nome, 
                "data": d_viagem.strftime('%d/%m/%Y'), # Garante gravação dd/mm/yyyy com barras
                "hora_saida": h_saida.strip(), 
                "trajeto": t_escolha, 
                "status": s_escolha,
                "centro_custo": "210301 - Moagem", 
                "hotel_v": v_hotel, 
                "comb_v": v_comb,
                "aereo_v": v_aereo, 
                "outros_v": v_outros, 
                "total": f"{v_total:.2f}", 
                "voo": ""
            }
            
            df_v = pd.concat([df_v, pd.DataFrame([novo_reg])], ignore_index=True)
            rp.update_file("dados_logistica.csv", "Logistics Base Auto-Update via Admin", df_v.to_csv(index=False), f_file.sha)
            st.success("Registro operacional persistido com sucesso na base de dados.")
            st.rerun()
        except ValueError:
            st.error("Erro: Certifique-se de que todos os valores informados nos campos de custos são numéricos.")

st.markdown("---")

# 4. TABELA DE AUDITORIA E VISUALIZAÇÃO GERAL DA BASE
st.markdown('<div class="section-header">Base de Dados Completa (Modo de Exibição e Auditoria)</div>', unsafe_allow_html=True)

# Configuração para forçar a exibição correta como campo de texto na tabela interativa
cfg_tabela = {"data": st.column_config.TextColumn("Data", required=True)}

df_v_editado = st.data_editor(df_v, column_config=cfg_tabela, hide_index=True, width='stretch', key="editor_corporativo_admin_v3")

if st.button("Salvar Modificações Diretas da Tabela", width='content'):
    rp.update_file("dados_logistica.csv", "Tabela Manual Update", df_v_editado.to_csv(index=False), rp.get_contents("dados_logistica.csv").sha)
    st.success("Modificações salvas diretamente no arquivo base.")
    st.rerun()
