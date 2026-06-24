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
    .obs-card { background-color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #FF7F50; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
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

# 🌟 NOVO CAMPO DE OBSERVAÇÕES EM CAIXA DE TEXTO MULTILINHA (TEXT_AREA)
st.markdown('<div class="section-header">Observações Semanais Operacionais</div>', unsafe_allow_html=True)
st.info("Digite as atividades abaixo. Você pode pressionar ENTER diretamente para quebrar linhas e organizar o texto.")

novas_observacoes = {}
# Criando abas para cada dia da semana para ficar limpo, organizado e gigante para escrever
abas = st.tabs([f"{dia} ({datas_s[i]})" for i, dia in enumerate(dias_s)])

for i, dia in enumerate(dias_s):
    with abas[i]:
        texto_antigo = obs_dict.get(dia.lower(), "")
        # O st.text_area aceita parágrafos, Enter, textos enormes e não esmaga nada
        conteudo = st.text_area(
            label=f"Instruções para {dia}:",
            value=texto_antigo,
            height=200,
            key=f"txt_obs_{dia.lower()}"
        )
        novas_observacoes[dia.lower()] = conteudo

# Botão único para salvar todas as observações de uma vez só
if st.button("Salvar Todas as Observações", width='stretch'):
    dados_salvar = []
    for i, dia in enumerate(dias_s):
        dados_salvar.append({
            "dia": dia,
            "data": datas_s[i],
            "observacao": novas_observacoes[dia.lower()]
        })
    df_novo_obs = pd.DataFrame(dados_salvar)
    rp.update_file("observacoes.csv", "Update Obs TextAreas", df_novo_obs.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
    st.success("Todas as observações foram salvas com sucesso!"); st.rerun()

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
        st.success("Status atualizado com sucesso."); st.rerun()

st.markdown("---")

# 5. FILTRAGEM DOS TRECHOS (APENAS AS 5 COLUNAS ORIGINAIS QUE VOCÊ PRECISA)
df_vis = df_v[df_v["status"] == "Confirmado"]
df_sem = df_vis[df_vis["data"].isin(datas_s)]

p_filter = st.multiselect("Filtrar visualização por Passageiro:", options=sorted(list(df_sem["passageiro"].unique())))
df_ex = df_sem[df_sem['passageiro'].isin(p_filter)] if p_filter else df_sem

n_col = {
    "passageiro": "Passageiro", 
    "data": "Data", 
    "horario": "Horário", 
    "saida": "Saída", 
    "motorista": "Motorista"
}

if "horario" not in df_ex.columns and "hora_saida" in df_ex.columns:
    df_ex = df_ex.rename(columns={"hora_saida": "horario"})

cols_finais = [c for c in ["passageiro", "data", "horario", "saida", "motorista"] if c in df_ex.columns]
df_lp = df_ex[cols_finais]

t_str = df_ex['trajeto'].str.strip().str.lower().str.replace("á", "a") if 'trajeto' in df_ex.columns else pd.Series()

df_pl = df_lp[t_str == "pontes e lacerda x cuiaba"].rename(columns=n_col)
df_cp = df_lp[t_str == "cuiaba x pontes e lacerda"].rename(columns=n_col)
df_out = df_lp[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")].rename(columns=n_col)

# 6. EXIBIÇÃO DAS TABELAS ORIGINAIS DE TRECHOS
st.markdown('<div class="treche-header">Trecho: Pontes e Lacerda x Cuiabá</div>', unsafe_allow_html=True)
st.dataframe(df_pl, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Trecho: Cuiabá x Pontes e Lacerda</div>', unsafe_allow_html=True)
st.dataframe(df_cp, width='stretch', hide_index=True)

st.markdown('<div class="treche-header">Outros Trajetos e Viagens Especiais</div>', unsafe_allow_html=True)
st.dataframe(df_out, width='stretch', hide_index=True)
