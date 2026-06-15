import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta
import zoneinfo

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False; st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

df_o.columns = df_o.columns.str.strip().str.lower()
df_o = df_o.loc[:, ~df_o.columns.duplicated()]

fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje_f = datetime.now(fuso).date()

st.write("### 📅 Período da Agenda")
data_sel = st.date_input("Escolha o dia:", value=hoje_f)

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

st.write("### 📝 Observações Semanais")
df_o_edit = st.data_editor(df_o_at, hide_index=True, width='stretch', key="ed_obs_v37")

if st.button("💾 Salvar Alterações", width='stretch'):
    rp.update_file("observacoes.csv", "Update", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.success("Salvo!"); st.rerun()

df_v.columns = df_v.columns.str.strip().str.lower()
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

# 🛡️ NOVA LÓGICA SEM ASPAS LONGAS NA VERIFICAÇÃO (Evita o corte da sincronização)
if "status" in df_v.columns:
    df_v["status"] = df_v["status"].fillna("")
else:
    df_v["status"] = ""

df_v = df_v.fillna("").astype(str)

# Filtra removendo o que foi cancelado ou ocultado de forma direta
df_vis = df_v[(df_v["status"] != "Cancelado") & (df_v["status"] != "Ocultado")]
df_sem = df_vis
