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

# CSS DA TELA
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

# 4. CAIXAS DE OBSERVAÇÕES
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

# 5. DADOS DE VIAGEM E MAQUIAGEM DE COLUNAS
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

def get_col(df, options):
    for o in options:
        if o in df.columns:
            return df[o].fillna("").astype(str)
    return pd.Series([""] * len(df), index=df.index)

if 'trajeto' in df_ex.columns:
    t_str = df_ex['trajeto'].str.strip().str.lower().str.replace("á", "a")
else:
    t_str = pd.Series([""] * len(df_ex), index=df_ex.index)

df_pl_raw = df_ex[t_str == "pontes e lacerda x cuiaba"]
df_cp_raw = df_ex[t_str == "cuiaba x pontes e lacerda"]
df_out_raw = df_ex[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")]

# Dataframes com MultiIndex
dict_pl = {
    ('', 'Passageiro'): get_col(df_pl_raw, ['passageiro']),
    ('Saída de P. Lacerda', 'semana'): get_col(df_pl_raw, ['semana']),
    ('Saída de P. Lacerda', 'data'): get_col(df_pl_raw, ['data']),
    ('Saída de P. Lacerda', 'horário'): get_col(df_pl_raw, ['horario', 'hora_saida']),
    ('Saída de P. Lacerda', 'saída'): get_col(df_pl_raw, ['saida']),
    ('Chegada em Cuiabá', 'Cia/nº voo'): get_col(df_pl_raw, ['cia/n voo', 'voo']),
    ('Chegada em Cuiabá', 'Horário Voo'): get_col(df_pl_raw, ['horario do voo', 'horario do vuo']),
    ('Chegada em Cuiabá', 'Data do Voo'): get_col(df_pl_raw, ['data do voo', 'data do vuo']),
    ('Chegada em Cuiabá', 'Destino'): get_col(df_pl_raw, ['destino', 'hotel em cuiaba']),
    ('', 'Motorista'): get_col(df_pl_raw, ['motorista'])
}
df_pl = pd.DataFrame(dict_pl)

dict_cp = {
    ('', 'Passageiro'): get_col(df_cp_raw, ['passageiro']),
    ('Chegada em Cuiabá', 'semana'): get_col(df_cp_raw, ['semana_ret']),
    ('Chegada em Cuiabá', 'data'): get_col(df_cp_raw, ['data_ret']),
    ('Chegada em Cuiabá', 'horário'): get_col(df_cp_raw, ['horario_ret', 'chegada do voo']),
    ('Chegada em Cuiabá', 'Cia/nº voo'): get_col(df_cp_raw, ['cia/n voo', 'voo']),
    ('Chegada em Cuiabá', 'Hotel'): get_col(df_cp_raw, ['hotel cuiaba']),
    ('Saída para P. Lacerda', 'semana'): get_col(df_cp_raw, ['semana']),
    ('Saída para P. Lacerda', 'data'): get_col(df_cp_raw, ['data']),
    ('Saída para P. Lacerda', 'horário'): get_col(df_cp_raw, ['horario', 'hora_saida']),
    ('Saída para P. Lacerda', 'Motorista'): get_col(df_cp_raw, ['motorista']),
    ('', 'Destino'): get_col(df_cp_raw, ['destino', 'hospedagem . lacerda'])
}
df_cp = pd.DataFrame(dict_cp)

# 6. GERADOR DE HTML COM BORDAS VISÍVEIS
def gerar_tabela_html(df, titulo):
    if df.empty:
        return f"<div class='titulo-bloco'>{titulo}</div><table style='background:#f4f4f4; border: 1px solid #777;'><tr><td>Sem viagens confirmadas.</td></tr></table>"
    
    html = f"<div class='titulo-bloco'>{titulo}</div><table style='border-collapse: collapse; border: 1px solid #777;'>"
    html += "<thead style='background-color: #1b294b; color: white;'>"
    
    # Cabeçalho Grupos
    html += "<tr>"
    for group, col in df.columns:
        html += f"<th style='border: 1px solid #777; padding: 6px;'>{group}</th>"
    html += "</tr>"
    
    # Cabeçalho Colunas
    html += "<tr>"
    for group, col in df.columns:
        html += f"<th style='border: 1px solid #777; padding: 6px;'>{col}</th>"
    html += "</tr></thead><tbody>"
    
    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td style='border: 1px solid #777; padding: 6px;'>{val}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

# [Restante do código de geração HTML e exibição st.dataframe idêntico...]
# (Note que o segredo aqui foi adicionar style='border: 1px solid #777' em todas as tags <table>, <th> e <td>)
