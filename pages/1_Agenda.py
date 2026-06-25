import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta
import zoneinfo

# 1. VERIFICAÇÃO DE LOGIN
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA LOGISTICS", layout="wide")

# CSS COM BORDAS DEFINIDAS
st.markdown("""<style>
    .stApp { background-color: #F8FAFC !important; }
    .main-title { color: #1b294b !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
    .section-header { background-color: #1b294b !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin: 15px 0; }
    .treche-header { background-color: #1b294b !important; color: white !important; padding: 6px 12px; font-weight: bold; font-size: 11pt; border-radius: 4px; margin: 20px 0 10px; }
</style>""", unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
tk = st.secrets["GITHUB_TOKEN"]
rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])
df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

# 3. CONTROLE DE DATAS
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
dias_s = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
segunda = datetime.now(fuso).date() - timedelta(days=datetime.now(fuso).date().weekday())
datas_s = [(segunda + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]

# 4. OBSERVAÇÕES (Abas com Enter)
st.markdown('<div class="section-header">Observações Semanais</div>', unsafe_allow_html=True)
obs_map = {row['dia'].strip().lower(): row['observacao'] for _, row in df_o.iterrows()}
novas_obs = {}
abas = st.tabs([f"{d} ({datas_s[i]})" for i, d in enumerate(dias_s)])
for i, dia in enumerate(dias_s):
    with abas[i]:
        novas_obs[dia.lower()] = st.text_area("Instruções:", value=obs_map.get(dia.lower(), ""), height=150)

if st.button("Salvar Observações"):
    df_new = pd.DataFrame([{"dia": d, "data": datas_s[i], "observacao": novas_obs[d.lower()]} for i, d in enumerate(dias_s)])
    rp.update_file("observacoes.csv", "Update", df_new.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.rerun()

# 5. FILTRAGEM E EXIBIÇÃO (Colunas Exatas)
df_v.columns = df_v.columns.str.strip().str.lower()
df_v = df_v[df_v['status'] == 'Confirmado']
df_sem = df_v[df_v['data'].isin(datas_s)]

def get_table(df, trajeto_nome):
    subset = df[df['trajeto'].str.strip().str.lower() == trajeto_nome.lower()]
    return subset[['passageiro', 'data', 'horario', 'saida', 'motorista', 'voo', 'horario do voo', 'data do voo', 'destino']]

df_pl = get_table(df_sem, "pontes e lacerda x cuiaba")
df_cp = get_table(df_sem, "cuiaba x pontes e lacerda")
df_out = df_sem[~df_sem['trajeto'].str.contains("pontes e lacerda", case=False)]

# 6. EXIBIÇÃO E PDF (Com bordas)
for title, df in [("P. Lacerda x Cuiabá", df_pl), ("Cuiabá x P. Lacerda", df_cp), ("Outros", df_out)]:
    st.markdown(f'<div class="treche-header">{title}</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

# Botão PDF
html = f"<html><style>table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 5px; }}</style><body>"
html += f"<h2>Agenda Aura</h2>" + df_pl.to_html() + df_cp.to_html() + df_out.to_html() + "</body></html>"
st.download_button("Baixar PDF/HTML", data=html, file_name="agenda.html", mime="text/html")
