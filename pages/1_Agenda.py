import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta
import zoneinfo

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

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

st.write("### 📝 Observações Semanais")
df_o_edit = st.data_editor(df_o_at, column_config={"dia": st.column_config.TextColumn("Dia", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "observacao": st.column_config.TextColumn("Observação", width="large")}, hide_index=True, width='stretch', row_height=100, key="ed_obs_v32")

if st.button("💾 Salvar Alterações das Observações", width='stretch'):
    rp.update_file("observacoes.csv", "Update", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.success("Salvo!"); st.rerun()

st.markdown("---")

df_v.columns = df_v.columns.str.strip().str.lower()
df_v = df_v.loc[:, ~df_v.columns.duplicated()]
if "status" not in df_v.columns: df_v["status"] = "Confirmado"
df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
df_v = df_v.fillna("").astype(str)

st.write("### ⚙️ Gerenciar Status de Viagens")
lista_g = [f"{i} - {row['passageiro']} ({row['data']}) [{row['status']}]" for i, row in df_v.iterrows() if row['passageiro'] != ""]
col_s, col_st = st.columns([2, 1])
v_sel = col_s.selectbox("Selecione a viagem:", options=[""] + lista_g)
n_st = col_st.selectbox("Mudar para:", ["Confirmado", "Cancelado", "Ocultado"])

if st.button("⚠️ Atualizar Status", width='stretch'):
    if v_sel:
        idx = int(v_sel.split(" - ")[0])
        df_v.at[idx, "status"] = n_st
        rp.update_file("dados_logistica.csv", "Status", df_v.to_csv(index=False), rp.get_contents("dados_logistica.csv").sha)
        st.success("Status updated!"); st.rerun()

st.markdown("---")

df_vis = df_v[df_v["status"] == "Confirmado"]
df_sem = df_vis[df_vis["data"].isin(datas_s)]

p_filter = st.multiselect("Filtrar por Passageiro:", options=sorted(list(df_sem["passageiro"].unique())))
df_ex = df_sem[df_sem['passageiro'].isin(p_filter)] if p_filter else df_sem

cols_ok = [c for c in df_ex.columns if "r$" not in c and "custo" not in c and "valor" not in c and "status" not in c]
df_lp = df_ex[cols_ok]

n_col = {"passageiro": "Passageiro", "trajeto": "Trajeto", "semana": "Semana", "data": "Data", "horario": "Horário", "saida": "Saída", "cia/nº voo": "Cia/Nº Voo", "horario do vuo": "Horário do Voo", "data do vuo": "Data do Voo", "hotel em cuiaba": "Hotel em Cuiabá", "hotel cuiaba": "Hotel Cuiabá", "motorista": "Motorista"}
t_str = df_lp['trajeto'].str.strip().str.lower().str.replace("á", "a")

df_pl = df_lp[t_str == "pontes e lacerda x cuiaba"].rename(columns=n_col)
df_cp = df_lp[t_str == "cuiaba x pontes e lacerda"].rename(columns=n_col)
df_out = df_lp[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")].rename(columns=n_col)

# 🔄 ESTRUTURAÇÃO DO DOCUMENTO DE IMPRESSÃO
def gerar_relatorio_html(dt_c, df_o_html, df_pl, df_cp):
    style = """
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; margin: 20px; font-size: 11px; line-height: 1.4; }
        .header { background: #FF7F50; color: white; text-align: center; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .header h2 { margin: 0; font-size: 18px; letter-spacing: 1px; }
        .meta { text-align: right; color: #777; font-size: 10px; margin-bottom: 10px; }
        h3 { background: #002D5E; color: white; padding: 6px 10px; border-radius: 4px; margin-top: 20px; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 15px; background: #fff; }
        th, td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; vertical-align: top; }
        th { background: #f5f5f5; color: #111; font-weight: bold; text-transform: uppercase; font-size: 10px; }
        tr:nth-child(even) { background: #fafafa; }
    </style>
    """
    html = f"<html><head><meta charset='utf-8'>{style}</head><body>"
    html += f"<div class='meta'>Emitido em: {dt_c}</div>"
    html += f"<div class='header'><h2>AURA LOGISTICS — AGENDA DA SEMANA</h2></div>"
    html += f"<h3>📝 OBSERVAÇÕES DA SEMANA</h3>{df_o_html.to_html(index=False, escape=False)}"
    html += f"<h3>🚍 TRECHO: PONTES E LACERDA X CUIABÁ</h3>{df_pl.to_html(index=False)}"
    html += f"<h3>🚍 TRECHO: CUIABÁ X PONTES E LACERDA</h3>{df_cp.to_html(index=False)}"
    html += "</body></html>"
    return html

dt_c = datetime.now(fuso).strftime('%d/%m/%Y às %H:%M')
df_o_html = df_o_edit.copy()
df_o_html["observacao"] = df_o_html["observacao"].astype(str).str.replace("\n", "<br>")

doc_final = gerar_relatorio_html(dt_c, df_o_html, df_pl, df_cp)

st.download_button(label="📄 Baixar Agenda Formatada (HTML/PDF)", data=doc_final, file_name="agenda_AURA.html", mime="text/html", width='stretch')

st.write("### 🚍 PONTES E LACERDA X CUIABÁ")
st.dataframe(df_pl, width='stretch', hide_index=True)

st.write("### 🚍 CUIABÁ X PONTES E LACERDA")
st.dataframe(df_cp, width='stretch', hide_index=True)

st.write("### 🔀 OUTROS TRAJETOS")
st.dataframe(df_out, width='stretch', hide_index=True)
