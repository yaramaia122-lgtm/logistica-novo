import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta
import zoneinfo

# 1. VERIFICAÇÃO DE SEGURANÇA E LOGIN
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

# 2. CONEXÃO COM O GITHUB REPOSITORY
tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

# 3. CARREGAMENTO DOS ARQUIVOS BASE
f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))
df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

# Limpeza preventiva de colunas duplicadas ou espaços
df_o.columns = df_o.columns.str.strip().str.lower()
df_o = df_o.loc[:, ~df_o.columns.duplicated()]

# 4. TRATAMENTO DO FUSO HORÁRIO E DATAS DA SEMANA
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje_f = datetime.now(fuso).date()

st.write("### 📅 Período da Agenda")
data_sel = st.date_input("Visualizar agenda a partir do dia:", value=hoje_f)

# Define a segunda-feira da semana escolhida
segunda = data_sel - timedelta(days=data_sel.weekday())
dias_s = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
datas_s = [(segunda + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]

try: 
    data_salva = str(df_o.iloc[0]["data"]).strip()
except: 
    data_salva = ""

# Sincroniza observações antigas ou limpa se for nova semana
obs_dict = {}
if data_salva == datas_s[0]:
    obs_dict = dict(zip(df_o["dia"].str.strip().str.lower(), df_o["observacao"].fillna("")))

dados_obs = []
for i, dia in enumerate(dias_s):
    dados_obs.append({"dia": dia, "data": datas_s[i], "observacao": obs_dict.get(dia.lower(), "")})
df_o_at = pd.DataFrame(dados_obs)

# 5. INTERFACE: EDITOR DE OBSERVAÇÕES
st.write("### 📝 Observações Semanais")
df_o_edit = st.data_editor(
    df_o_at, 
    column_config={
        "dia": st.column_config.TextColumn("Dia", disabled=True), 
        "data": st.column_config.TextColumn("Data", disabled=True), 
        "observacao": st.column_config.TextColumn("Observação", width="large")
    }, 
    hide_index=True, 
    width='stretch', 
    row_height=100, 
    key="ed_obs_oficial_v1"
)

if st.button("💾 Salvar Alterações das Observações", width='stretch'):
    rp.update_file("observacoes.csv", "Update Obs", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.success("Observações salvas com sucesso!"); st.rerun()

st.markdown("---")

# 6. INTERFACE: GERENCIADOR DE STATUS DAS VIAGENS
df_v.columns = df_v.columns.str.strip().str.lower()
df_v = df_v.loc[:, ~df_v.columns.duplicated()]
if "status" not in df_v.columns: 
    df_v["status"] = "Confirmado"
df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
df_v = df_v.fillna("").astype(str)

st.write("### ⚙️ Gerenciar Status de Viagens")
lista_g = [f"{i} - {row['passageiro']} ({row['data']}) [{row['status']}]" for i, row in df_v.iterrows() if row['passageiro'] != ""]
col_s, col_st = st.columns(
