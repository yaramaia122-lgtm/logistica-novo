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

# CSS DA TELA (SEGURO CONTRA ERROS)
css_tela = "<style>"
css_tela += ".stApp { background-color: #F8FAFC !important; }"
css_tela += ".main-title { color: #1b294b !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }"
css_tela += ".subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }"
css_tela += ".section-header { background-color: #1b294b !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }"
css_tela += ".treche-header { background-color: #1b294b !important; color: white !important; padding: 6px 12px; font-weight: bold; font-size: 11pt; border-radius: 4px; margin-top: 20px; margin-bottom: 10px; }"
css_tela += "</style>"
st.markdown(css_tela, unsafe_allow_html=True)

st.markdown('<div class="main-title">Agenda Semanal de Transporte</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualização integrada de trechos, programações confirmadas e orientações</div>', unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
tk = st.secrets["GITHUB_TOKEN"]
repo = st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))
f_obs = rp.get_contents("observacoes.csv")
df_o = pd.read_csv(io.StringIO(f_obs.decoded_content.decode()))

df_o.columns = df_o.columns.str.strip().str.lower()
df_o = df_o.loc[:, ~df_o.columns.duplicated()]

# 3. CONTROLE DE DATAS
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje_f = datetime.now(fuso).date()

st.write("### Período de Monitoramento")
data_sel = st.date_input("Visualizar agenda a partir do dia:", value=hoje_f)

segunda = data_sel - timedelta(days=data_sel.weekday())
dias_s = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
datas_s = [(segunda + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]

try:
    data_salva = str(df_o.iloc[0]["data"]).strip()
except:
    data_salva = ""

obs_dict = {}
if data_salva == datas_s[0]:
    obs_dict = dict(zip(df_o["dia"].str.strip().str.lower(), df_o["observacao"].fillna("")))

# 🌟 4. CAIXAS DE OBSERVAÇÕES (COM ESPAÇO PARA ALT+ENTER)
st.markdown('<div class="section-header">Observações Semanais Operacionais</div>', unsafe_allow_html=True)

novas_observacoes = {}
titulos_abas = []
for i, dia in enumerate(dias_s):
    titulos_abas.append(dia + " (" + datas_s[i] + ")")

abas = st.tabs(titulos_abas)

for i, dia in enumerate(dias_s):
    with abas[i]:
        texto_antigo = obs_dict.get(dia.lower(), "")
        conteudo = st.text_area(label="Atividades para " + dia + ":", value=texto_antigo, height=180, key="txt_obs_" + dia.lower())
        novas_observacoes[dia.lower()] = conteudo

if st.button("💾 Salvar Todas as Observações", width='stretch'):
    dados_salvar = []
    for i, dia in enumerate(dias_s):
        dados_salvar.append({"dia": dia, "data": datas_s[i], "observacao": novas_observacoes[dia.lower()]})
    df_novo_obs = pd.DataFrame(dados_salvar)
    rp.update_file("observacoes.csv", "Update Obs TextAreas", df_novo_obs.to_csv(index=False), f_obs.sha)
    st.success("Observações salvas com sucesso!")
    st.rerun()

st.markdown("---")

# 5. DADOS DE VIAGEM (RECUPERANDO TODAS AS COLUNAS)
df_v.columns = df_v.columns.str.strip().str.lower()
df_v.columns = df_v.columns.str.replace("á", "a").str.replace("í", "i").str.replace("º", "")
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

if "status" not in df_v.columns:
    df_v["status"] = "Confirmado"
df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
df_v = df_v.fillna("").astype(str)

df_vis = df_v[df_v["status"] == "Confirmado"]
df_sem = df_vis[df_vis["data"].isin(datas_s)]

p_filter = st.multiselect("Filtrar visualização por Passageiro:", options=sorted(list(df_sem["passageiro"].unique())))
if p_filter:
    df_ex = df_sem[df_sem['passageiro'].isin(p_filter)]
else:
    df_ex = df_sem

# MAPEAMENTO DE COLUNAS COMPLETAS E BONITAS PARA O PDF
n_col = {
    "centro_custo": "Centro de Custo",
    "passageiro": "Passageiro",
    "semana": "Semana",
    "data": "Data",
    "horario": "Horário",
    "hora_saida": "Horário",
    "saida": "Saída",
    "cia/n voo": "Cia/Nº Voo",
    "horario do vuo": "Horário Voo",
    "data do vuo": "Data Voo",
    "hotel em cuiaba": "Hotel Cuiabá",
    "hotel cuiaba": "Hotel Cuiabá",
    "motorista": "Motorista"
}

# Retirando colunas financeiras, mas mantendo as essenciais da imagem
cols_ok = []
for c in df_ex.columns:
    if "r$" not in c and "custo" not in c and "valor" not in c and "status" not in c:
        cols_ok.append(c)
    elif c == "centro_custo": # Garante que o Centro de Custo apareça como na sua imagem
        cols_ok.append(c)

df_lp = df_ex[cols_ok]

if 'trajeto' in df_ex.columns:
    t_str = df_ex['trajeto'].str.strip().str.lower().str.replace("á", "a")
else:
    t_str = pd.Series([""] * len(df_ex), index=df_ex.index)

df_pl = df_lp[t_str == "pontes e lacerda x cuiaba"].rename(columns=n_col)
df_cp = df_lp[t_str == "cuiaba x pontes e lacerda"].rename(columns=n_col)
df_out = df_lp[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")].rename(columns=n_col)

# 🌟 6. GERADOR DE HTML IDÊNTICO À PLANILHA AURA (AZUL E CORAL)
dt_c = datetime.now(fuso).strftime('%d/%m/%Y às %H:%M')

# CSS Embutido diretamente na string para formatar o download
css_html = "<style>"
css_html += "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 11px; padding: 20px; color: #000; }"
css_html += "table { width: 100%; border-collapse: collapse; margin-bottom: 25px; border: 1px solid #777; }"
css_html += "th, td { border: 1px solid #777; padding: 6px; text-align: center; vertical-align: middle; }"
css_html += "thead th { background-color: #1b294b; color: #ffffff; font-weight: normal; font-size: 11px; }" # Azul Escuro
css_html += ".titulo-bloco { background-color: #1b294b; color: white; padding: 10px; font-size: 14px; font-weight: bold; text-align: left; }"
css_html += ".obs-header { background-color: #ef5350; color: white; padding: 8px; font-size: 14px; font-weight: bold; text-align: center; border: 1px solid #777; }" # Coral
css_html += ".obs-dia { width: 15%; font-weight: bold; background-color: #f8f9fa; }"
css_html += ".obs-texto { text-align: left; padding-left: 10px; line-height: 1.4; }"
css_html += "</style>"

html_doc = "<html><head><meta charset='utf-8'>" + css_html + "</head><body>"
html_doc += "<div style='text-align: right; color: #555; font-size: 10px; margin-bottom: 10px;'>Emitido em: " + dt_c + "</div>"

# Tabela PL x Cuiabá
html_doc += "<div class='titulo-bloco'>Pontes e Lacerda x Cuiabá</div>"
if not df_pl.empty:
    html_doc += df_pl.to_html(index=False, justify='center', na_rep='-')
else:
    html_doc += "<table style='background:#f4f4f4;'><tr><td>Sem viagens confirmadas para este trecho na semana.</td></tr></table>"

# Tabela Cuiabá x PL
html_doc += "<div class='titulo-bloco' style='margin-top: 20px;'>Cuiabá x Pontes e Lacerda</div>"
if not df_cp.empty:
    html_doc += df_cp.to_html(index=False, justify='center', na_rep='-')
else:
    html_doc += "<table style='background:#f4f4f4;'><tr><td>Sem viagens confirmadas para este trecho na semana.</td></tr></table>"

# Tabela Formata de Observações
html_doc += "<table style='margin-top: 30px;'>"
html_doc += "<tr><td colspan='2' class='obs-header'>Observações</td></tr>"

for dia in dias_s:
    idx = dias_s.index(dia)
    data_formatada = datas_s[idx]
    texto_puro = novas_observacoes[dia.lower()]
    
    # Substitui Enter real por <br> do HTML para não perder a formatação
    texto_html = texto_puro.replace("\n", "<br>")
    
    html_doc += "<tr>"
    html_doc += "<td class='obs-dia'>" + dia + "<br>" + data_formatada + "</td>"
    html_doc += "<td class='obs-texto'>" + texto_html + "</td>"
    html_doc += "</tr>"
html_doc += "</table>"

html_doc += "</body></html>"

st.download_button(label="📄 Baixar Relatório Corporativo AURA (HTML/PDF)", data=html_doc, file_name="agenda_AURA_semanal.html", mime="text/html", width='stretch')

# 7. EXIBIÇÃO NO PAINEL
st.markdown('<div class="treche-header">Trecho: Pontes e Lacerda x Cuiabá</div>', unsafe_allow_html=True)
st.dataframe(df_pl, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Trecho: Cuiabá x Pontes e Lacerda</div>', unsafe_allow_html=True)
st.dataframe(df_cp, width='stretch', hide_index=True)
