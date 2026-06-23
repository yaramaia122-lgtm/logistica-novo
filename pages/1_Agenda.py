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

# 🛠️ AJUSTE CRÍTICO: Configuração da coluna com suporte para texto longo multilinha expansível
cfg_col = {
    "dia": st.column_config.TextColumn("Dia da Semana", disabled=True), 
    "data": st.column_config.TextColumn("Data", disabled=True), 
    "observacao": st.column_config.TextColumn(
        "Instruções / Observações (Dê duplo clique para expandir textas longas)", 
        width="large", 
        disabled=False
    )
}

# row_height=130 dá mais espaço vertical nativo para as 3 linhas aparecerem de imediato
df_o_edit = st.data_editor(
    df_o_at, 
    column_config=cfg_col, 
    hide_index=True, 
    width='stretch', 
    row_height=130, 
    key="ed_obs_corp_v11"
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
        rp.update_file("dados_logistica.csv", "Status Update", df_v.to_csv(index=False), f_log.sha)
        st.success("Status updated."); st.rerun()

st.markdown("---")

# 5. FILTRAGEM DOS TRECHOS
df_vis = df_v[df_v["status"] == "Confirmado"]
df_sem = df_vis[df_vis["data"].isin(datas_s)]

p_filter = st.multiselect("Filtrar visualização por Passageiro:", options=sorted(list(df_sem["passageiro"].unique())))
df_ex = df_sem[df_sem['passageiro'].isin(p_filter)] if p_filter else df_sem

cols_ok = [c for c in df_ex.columns if "r$" not in c and "custo" not in c and "valor" not in c and "status" not in c]
df_lp = df_ex[cols_ok]

n_col = {"passageiro": "Passageiro", "trajeto": "Trajeto", "semana": "Semana", "data": "Data", "horario": "Horário", "saida": "Saída", "cia/n voo": "Cia/Nº Voo", "horario do vuo": "Horário do Voo", "data do vuo": "Data do Voo", "hotel em cuiaba": "Hotel em Cuiabá", "hotel cuiaba": "Hotel Cuiabá", "motorista": "Motorista"}
t_str = df_lp['trajeto'].str.strip().str.lower().str.replace("á", "a")

df_pl = df_lp[t_str == "pontes e lacerda x cuiaba"].rename(columns=n_col)
df_cp = df_lp[t_str == "cuiaba x pontes e lacerda"].rename(columns=n_col)
df_out = df_lp[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")].rename(columns=n_col)

# 6. CONSTRUÇÃO DO DOCUMENTO HTML
dt_c = datetime.now(fuso).strftime('%d/%m/%Y às %H:%M')
df_o_html = df_o_edit.copy()
df_o_html["observacao"] = df_o_html["observacao"].astype(str).str.replace("\n", "<br>")

doc_final = "<html><body style='font-family:Arial,sans-serif;padding:20px;color:#333;'>"
doc_final += "<div style='text-align:right;color:#666;font-size:10px;'>Emitido em: " + dt_c + "</div>"
doc_final += "<h2 style='background-color:#FF7F50;color:white;padding:12px;text-align:center;'>AURA LOGISTICS — AGENDA SEMANAL</h2>"
doc_final += "<h3 style='background-color:#002D5E;color:white;padding:6px;font-size:12pt;'>OBSERVAÇÕES OPERACIONAIS</h3>" + df_o_html.to_html(index=False, escape=False)
doc_final += "<h3 style='background-color:#002D5E;color:white;padding:6px;font-size:12pt;'>TRECHO: PONTES E LACERDA X CUIABÁ</h3>" + df_pl.to_html(index=False)
doc_final += "<h3 style='background-color:#002D5E;color:white;padding:6px;font-size:12pt;'>TRECHO: CUIABÁ X PONTES E LACERDA</h3>" + df_cp.to_html(index=False)
doc_final += "</body></html>"

st.download_button(
    label="📄 Baixar Relatório de Agenda Formatado (HTML/PDF)", 
    data=doc_final, 
    file_name="agenda_AURA_semanal.html", 
    mime="text/html", 
    width='stretch'
)

# 7. EXIBIÇÃO DAS TABELAS NA TELA
st.markdown('<div class="treche-header">Trecho: Pontes e Lacerda x Cuiabá</div>', unsafe_allow_html=True)
st.dataframe(df_pl, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Trecho: Cuiabá x Pontes e Lacerda</div>', unsafe_allow_html=True)
st.dataframe(df_cp, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Outros Trajetos e Viagens Especiais</div>', unsafe_allow_html=True)
st.dataframe(df_out, width='stretch', hide_index=True)
