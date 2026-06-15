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

st.set_page_config(page_title="Agenda - AURA", layout="wide")

# 🎨 IDENTIDADE VISUAL DA AURA RESTAURADA (CORAL E AZUL ESCURO)
st.markdown("""<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .treche-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; border-radius: 4px; margin-top: 12px; }
</style>""", unsafe_allow_html=True)

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

# HEADERS EM CORAL DA TELA
st.markdown('<div class="agenda-header">Observações Semanais</div>', unsafe_allow_html=True)
df_o_edit = st.data_editor(
    df_o_at, 
    column_config={
        "dia": st.column_config.TextColumn("Dia da Semana", disabled=True), 
        "data": st.column_config.TextColumn("Data", disabled=True), 
        "observacao": st.column_config.TextColumn("Observação", width="large", disabled=False)
    }, 
    hide_index=True, 
    width='stretch', 
    row_height=100, 
    key="ed_obs_oficial_aurav7"
)

if st.button("💾 Salvar Alterações das Observações", width='stretch'):
    rp.update_file("observacoes.csv", "Update Obs", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.success("Observações salvas com sucesso!"); st.rerun()

st.markdown("---")

# 4. LIMPEZA E PADRONIZAÇÃO COMPATÍVEL COM PYTHON 3.14
df_v.columns = df_v.columns.str.strip().str.lower()
df_v.columns = df_v.columns.str.replace("á", "a").str.replace("í", "i").str.replace("º", "")
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

# Evita o uso de aspas aninhadas que quebram o compilador novo
if "status" in df_v.columns:
    df_v = df_v.fillna("")
else:
    df_v["status"] = "Confirmado"
    df_v = df_v.fillna("")

# 5. GERENCIADOR DE STATUS
st.write("### ⚙️ Gerenciar Status de Viagens")
lista_g = [f"{i} - {row['passageiro']} ({row['data']}) [{row['status']}]" for i, row in df_v.iterrows() if str(row['passageiro']).strip() != ""]
col_s, col_st = st.columns([2, 1])
v_sel = col_s.selectbox("Selecione a viagem para alterar:", options=[""] + lista_g)
n_st = col_st.selectbox("Mudar status para:", ["Confirmado", "Cancelado", "Ocultado"])

if st.button("⚠️ Atualizar Status da Viagem", width='stretch'):
    if v_sel:
        idx = int(v_sel.split(" - ")[0])
        df_v.at[idx, "status"] = n_st
        rp.update_file("dados_logistica.csv", "Status Update", df_v.to_csv(index=False), f_log.sha)
        st.success("Status atualizado com sucesso!"); st.rerun()

st.markdown("---")

# 6. FILTRAGEM INTELIGENTE SEM RISCOS DE SINTAXE
# Usando o método query para blindar o código contra o bug de aspas do interpretador
df_vis = df_v.query("status == 'Confirmado'")
df_sem = df_vis[df_vis["data"].isin(datas_s)]

p_filter = st.multiselect("Filtrar por Passageiro da Semana:", options=sorted(list(df_sem["passageiro"].unique())))
df_ex = df_sem[df_sem['passageiro'].isin(p_filter)] if p_filter else df_sem

cols_ok = [c for c in df_ex.columns if "r$" not in c and "custo" not in c and "valor" not in c and "status" not in c]
df_lp = df_ex[cols_ok]

n_col = {
    "passageiro": "Passageiro", "trajeto": "Trajeto", "semana": "Semana", 
    "data": "Data", "horario": "Horário", "saida": "Saída", 
    "cia/n voo": "Cia/Nº Voo", "horario do vuo": "Horário do Voo", 
    "data do vuo": "Data do Voo", "hotel em cuiaba": "Hotel em Cuiabá", 
    "hotel cuiaba": "Hotel Cuiabá", "motorista": "Motorista"
}

# Separação limpa dos trechos usando query
df_lp["trajeto_limpo"] = df_lp["trajeto"].astype(str).str.strip().str.lower().str.replace("á", "a")
df_pl = df_lp.query("trajeto_limpo == 'pontes e lacerda x cuiaba'").rename(columns=n_col).drop(columns=["trajeto_limpo"], errors="ignore")
df_cp = df_lp.query("trajeto_limpo == 'cuiaba x pontes e lacerda'").rename(columns=n_col).drop(columns=["trajeto_limpo"], errors="ignore")
df_out = df_lp.query("trajeto_limpo != 'pontes e lacerda x cuiaba' and trajeto_limpo != 'cuiaba x pontes e lacerda'").rename(columns=n_col).drop(columns=["trajeto_limpo"], errors="ignore")

# 7. CONSTRUÇÃO DO RELATÓRIO VISUAL HTML/PDF (MÉTODO ULTRA-SEGURO POR CONCATENAÇÃO)
dt_c = datetime.now(fuso).strftime('%d/%m/%Y às %H:%M')
df_o_html = df_o_edit.copy()
df_o_html["observacao"] = df_o_html["observacao"].astype(str).str.replace("\n", "<br>")

doc_final = "<html><body style='font-family:Arial,sans-serif;padding:20px;font-size:12px;color:#333;'>"
doc_final += "<div style='text-align:right;color:#666;font-size:10px;'>Emitido em: " + dt_c + "</div>"
doc_final += "<h2 style='background:#FF7F50;color:white;padding:12px;text-align:center;border-radius:6px;margin-bottom:20px;'>AURA LOGISTICS — AGENDA</h2>"
doc_final += "<h3 style='background:#002D5E;color:white;padding:6px;font-size:12px;border-radius:4px;'>📝 OBSERVAÇÕES DA SEMANA</h3>" + df_o_html.to_html(index=False, escape=False)
doc_final += "<h3 style='background:#002D5E;color:white;padding:6px;font-size:12px;border-radius:4px;'>🚍 PONTES E LACERDA X CUIABÁ</h3>" + df_pl.to_html(index=False)
doc_final += "<h3 style='background:#002D5E;color:white;padding:6px;font-size:12px;border-radius:4px;'>🚍 CUIABÁ X PONTES E LACERDA</h3>" + df_cp.to_html(index=False)
doc_final += "</body></html>"

st.download_button(label="📄 Baixar Relatório Otimizado (HTML/PDF 1 Página)", data=doc_final, file_name="agenda_AURA.html", mime="text/html", width='stretch')

# 8. EXIBIÇÃO DAS TABELAS COM OS HEADERS AZUIS DA AURA ORIGINAIS
st.markdown('<div class="treche-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
st.dataframe(df_pl, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
st.dataframe(df_cp, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
st.dataframe(df_out, width='stretch', hide_index=True)
