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

# 🎨 ESTILIZAÇÃO VISUAL ORIGINAL (CORAL E AZUL)
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

# 3. CONTROLE INTELIGENTE DE DATAS
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

# TÍTULO EM CORAL ORIGINAL
st.markdown('<div class="agenda-header">Observações Semanais</div>', unsafe_allow_html=True)

# 📌 REENGENHARIA VISUAL: Substitui a tabela travada por inputs de texto flexíveis
novas_obs = {}
with st.expander("📋 Clique aqui para visualizar e digitar as Observações do Período", expanded=True):
    for i, dia in enumerate(dias_s):
        # Cria uma caixa de texto grande para cada dia que aceita múltiplas linhas visíveis
        texto_padrao = obs_dict.get(dia.lower(), "")
        label_campo = f"{dia} ({datas_s[i]})"
        novas_obs[dia.lower()] = st.text_area(label_campo, value=texto_padrao, height=85, key=f"obs_{dia.lower()}_v3")

if st.button("💾 Salvar Alterações das Observações", width='stretch'):
    # Remonta o arquivo para gravação
    dados_salvar = []
    for i, dia in enumerate(dias_s):
        dados_salvar.append({
            "dia": dia,
            "data": datas_s[i],
            "observacao": novas_obs[dia.lower()].strip()
        })
    df_o_pronto = pd.DataFrame(dados_salvar)
    rp.update_file("observacoes.csv", "Update Obs", df_o_pronto.to_csv(index=False), rp.get_contents("observacoes.csv").
