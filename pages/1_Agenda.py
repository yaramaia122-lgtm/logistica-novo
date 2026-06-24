import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta
import zoneinfo

# 1. VERIFICAÇÃO DE LOGIN DE USUÁRIO
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA LOGISTICS", layout="wide")

# 🎨 ESTILIZAÇÃO CORPORATIVA PROFISSIONAL
st.markdown("""<style>
    .stApp { background-color: #F8FAFC !important; }
    .main-title { color: #002D5E !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
    .subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }
    .section-header { background-color: #002D5E !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }
    .treche-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; font-size: 11pt; border-radius: 4px; margin-top: 20px; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Agenda Semanal de Transporte</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualização integrada de trechos, programações confirmadas e orientações para motoristas</div>', unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))
df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

df_o.columns = df_o.columns.str.strip().str.lower()
df_o = df_o.loc[:, ~df_o.columns.duplicated()]

# 3. CONTROLE DE DATAS DA SEMANA
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje_f = datetime.now(fuso).date()

st.write("### Período de Monitoramento")
data_sel = st.date_input("Visualizar agenda a partir do dia:", value=hoje_f)

segunda = data_sel - timedelta(days=data_sel.weekday())
dias_s = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
datas_s = [(segunda + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]

try: data_salva = str(df_o.iloc[0]["data"]).strip()
except: data_salva = ""

obs_dict = {}
if data_salva == datas_s[0]:
    obs_dict = dict(zip(df_o["dia"].str.strip().str.lower(), df_o["observacao"].fillna("")))

dados_obs = []
for i, dia in enumerate(dias_s):
    dados_obs.append({"dia": dia, "data": datas_s[i], "observacao": obs_dict.get(dia.lower(), "")})
df_o_at = pd.DataFrame(dados_obs)

st.markdown('<div class="section-header">Observações Semanais Operacionais</div>', unsafe_allow_html=True)

# 🛠️ AJUSTE PERFEITO: st.column_config.TextColumn com form_input larga remove o limite de 1 linha
cfg_col = {
    "dia": st.column_config.TextColumn("Dia da Semana", disabled=True), 
    "data": st.column_config.TextColumn("Data", disabled=True), 
    "observacao": st.column_config.TextColumn(
        "Instruções / Observações", 
        width="large", 
        disabled=False
    )
}

# Mantive a tabela original exatamente como estava antes
df_o_edit = st.data_editor(
    df_o_at, 
    column_config=cfg_col, 
    hide_index=True, 
    width='stretch', 
    key="ed_obs_original_restaurado"
)

if st.button("Salvar Alterações das Observações", width='stretch'):
    rp.update_file("observacoes.csv", "Update Obs", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.success("Alterações salvas com sucesso."); st.rerun()

st.markdown("---")

# 4. TRATAMENTO DOS DADOS DE VIAGEM
df_v.columns = df_v.columns.str.strip().str.lower()
df_v.columns = df_v.columns.str.replace("á", "a").str.replace("í", "i").str.replace("º", "")
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

if "status" not in df_v.columns: df_v["status"] = "Confirmado"
df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
df_v = df_v.fillna("").astype(str)

st.write("### Gerenciamento de Status")
lista_g = [f"{i} - {row['passageiro']} ({row['data']}) [{row['status']}]" for i, row in df_v.iterrows() if str(row['passageiro']).strip() != ""]
col_s, col_st = st.columns([2, 1])
v_sel = col_s.selectbox("Selecione a viagem para alteração de status:", options=[""] + lista_g)
n_st = col_st.selectbox("Novo status:", ["Confirmado", "Cancelado", "Ocultado"])

if st.button("Atualizar Status do Registro Selecionado", width='stretch'):
    if v_sel:
        idx = int(v_sel.split(" - ")[0])
        df_v.at[idx, "status"] = n_st
        rp.update_file("dados_logistica.csv", "
