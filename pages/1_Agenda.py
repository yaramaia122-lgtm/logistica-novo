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

# 2. CSS ESCRITO DE FORMA SEGURA (SEM ASPAS TRIPLAS PARA EVITAR BUGS DO SERVIDOR)
css = "<style>"
css += ".stApp { background-color: #F8FAFC !important; }"
css += ".main-title { color: #002D5E !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }"
css += ".subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }"
css += ".section-header { background-color: #002D5E !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }"
css += ".treche-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; font-size: 11pt; border-radius: 4px; margin-top: 20px; margin-bottom: 10px; }"
css += "</style>"
st.markdown(css, unsafe_allow_html=True)

st.markdown('<div class="main-title">Agenda Semanal de Transporte</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualização integrada de trechos, programações confirmadas e orientações para motoristas</div>', unsafe_allow_html=True)

# 3. CONEXÃO GITHUB
tk = st.secrets["GITHUB_TOKEN"]
repo = st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))
f_obs = rp.get_contents("observacoes.csv")
df_o = pd.read_csv(io.StringIO(f_obs.decoded_content.decode()))

df_o.columns = df_o.columns.str.strip().str.lower()
df_o = df_o.loc[:, ~df_o.columns.duplicated()]

# 4. CONTROLE DE DATAS DA SEMANA
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

# 🌟 CAMPO DE OBSERVAÇÕES EM CAIXA DE TEXTO (ACEITA ENTER PARA PULAR LINHA)
st.markdown('<div class="section-header">Observações Semanais Operacionais</div>', unsafe_allow_html=True)
st.info("Digite as atividades abaixo. Pode pressionar ENTER diretamente para quebrar linhas.")

novas_observacoes = {}
titulos_abas = []
for i, dia in enumerate(dias_s):
    titulos_abas.append(dia + " (" + datas_s[i] + ")")

abas = st.tabs(titulos_abas)

for i, dia in enumerate(dias_s):
    with abas[i]:
        texto_antigo = obs_dict.get(dia.lower(), "")
        conteudo = st.text_area(label="Instruções para " + dia + ":", value=texto_antigo, height=150, key="txt_obs_" + dia.lower())
        novas_observacoes[dia.lower()] = conteudo

# Botão para salvar observações
if st.button("Salvar Todas as Observações", width='stretch'):
    dados_salvar = []
    for i, dia in enumerate(dias_s):
        dados_salvar.append({"dia": dia, "data": datas_s[i], "observacao": novas_observacoes[dia.lower()]})
    df_novo_obs = pd.DataFrame(dados_salvar)
    rp.update_file("observacoes.csv", "Update Obs TextAreas", df_novo_obs.to_csv(index=False), f_obs.sha)
    st.success("Todas as observações foram salvas com sucesso!")
    st.rerun()

st.markdown("---")

# 5. TRATAMENTO DOS DADOS DE VIAGEM
df_v.columns = df_v.columns.str.strip().str.lower()
df_v.columns = df_v.columns.str.replace("á", "a").str.replace("í", "i").str.replace("º", "")
df_v = df_v.loc[:, ~df_v.columns.duplicated()]

if "status" not in df_v.columns:
    df_v["status"] = "Confirmado"
df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
df_v = df_v.fillna("").astype(str)

st.write("### Gerenciamento de Status")
lista_g = []
for i, row in df_v.iterrows():
    if str(row['passageiro']).strip() != "":
        lista_g.append(str(i) + " - " + str(row['passageiro']) + " (" + str(row['data']) + ") [" + str(row['status']) + "]")

col_s, col_st = st.columns([2, 1])
v_sel = col_s.selectbox("Selecione a viagem para alteração de status:", options=[""] + lista_g)
n_st = col_st.selectbox("Novo status:", ["Confirmado", "Cancelado", "Ocultado"])

if st.button("Atualizar Status do Registro Selecionado", width='stretch'):
    if v_sel:
        idx = int(v_sel.split(" - ")[0])
        df_v.at[idx, "status"] = n_st
        rp.update_file("dados_logistica.csv", "Status Update", df_v.to_csv(index=False), f_log.sha)
        st.success("Status atualizado com sucesso.")
        st.rerun()

st.markdown("---")

# 6. FILTRAGEM DOS TRECHOS E TABELAS COM APENAS 5 COLUNAS
df_vis = df_v[df_v["status"] == "Confirmado"]
df_sem = df_vis[df_vis["data"].isin(datas_s)]

lista_passageiros = sorted(list(df_sem["passageiro"].unique()))
p_filter = st.multiselect("Filtrar visualização por Passageiro:", options=lista_passageiros)

if p_filter:
    df_ex = df_sem[df_sem['passageiro'].isin(p_filter)]
else:
    df_ex = df_sem

n_col_mapeamento = {"passageiro": "Passageiro", "data": "Data", "horario": "Horário", "saida": "Saída", "motorista": "Motorista"}

if "horario" not in df_ex.columns and "hora_saida" in df_ex.columns:
    df_ex = df_ex.rename(columns={"hora_saida": "horario"})

colunas_finais_existentes = []
for c in ["passageiro", "data", "horario", "saida", "motorista"]:
    if c in df_ex.columns:
        colunas_finais_existentes.append(c)

df_filtrado_colunas = df_ex[colunas_finais_existentes]

if 'trajeto' in df_ex.columns:
    t_str = df_ex['trajeto'].str.strip().str.lower().str.replace("á", "a")
else:
    t_str = pd.Series([""] * len(df_ex), index=df_ex.index)

df_pl = df_filtrado_colunas[t_str == "pontes e lacerda x cuiaba"].rename(columns=n_col_mapeamento)
df_cp = df_filtrado_colunas[t_str == "cuiaba x pontes e lacerda"].rename(columns=n_col_mapeamento)
df_out = df_filtrado_colunas[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")].rename(columns=n_col_mapeamento)

if df_pl.empty:
    df_pl = pd.DataFrame(columns=["Passageiro", "Data", "Horário", "Saída", "Motorista"])
if df_cp.empty:
    df_cp = pd.DataFrame(columns=["Passageiro", "Data", "Horário", "Saída", "Motorista"])
if df_out.empty:
    df_out = pd.DataFrame(columns=["Passageiro", "Data", "Horário", "Saída", "Motorista"])

# 🌟 7. RETORNO DA OPÇÃO DE SALVAR EM PDF/HTML (ESCRITA DE FORMA SEGURA)
dt_c = datetime.now(fuso).strftime('%d/%m/%Y às %H:%M')

dados_html_obs = []
for dia in dias_s:
    texto_formatado = novas_observacoes.get(dia.lower(), "").replace("\n", "<br>")
    idx_dia = dias_s.index(dia)
    dados_html_obs.append({"Dia da Semana": dia, "Data": datas_s[idx_dia], "Instruções / Observações": texto_formatado})
df_obs_relatorio = pd.DataFrame(dados_html_obs)

doc_final = "<html><body style='font-family:Arial,sans-serif;padding:20px;color:#333;'>"
doc_final += "<div style='text-align:right;color:#666;font-size:10px;'>Emitido em: " + dt_c + "</div>"
doc_final += "<h2 style='background-color:#FF7F50;color:white;padding:12px;text-align:center;'>AURA LOGISTICS — AGENDA SEMANAL</h2>"
doc_final += "<h3>OBSERVAÇÕES OPERACIONAIS</h3>" + df_obs_relatorio.to_html(index=False, escape=False)
doc_final += "<h3>TRECHO: PONTES E LACERDA X CUIABÁ</h3>" + df_pl.to_html(index=False)
doc_final += "<h3>TRECHO: CUIABÁ X PONTES E LACERDA</h3>" + df_cp.to_html(index=False)
doc_final += "</body></html>"

st.download_button(label="📄 Baixar Relatório de Agenda Formatado (HTML/PDF)", data=doc_final, file_name="agenda_AURA_semanal.html", mime="text/html", width='stretch')

# 8. EXIBIÇÃO EXCLUSIVA DAS TABELAS NA TELA
st.markdown('<div class="treche-header">Trecho: Pontes e Lacerda x Cuiabá</div>', unsafe_allow_html=True)
st.dataframe(df_pl, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Trecho: Cuiabá x Pontes e Lacerda</div>', unsafe_allow_html=True)
st.dataframe(df_cp, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Outros Trajetos e Viagens Especiais</div>', unsafe_allow_html=True)
st.dataframe(df_out, width='stretch', hide_index=True)
