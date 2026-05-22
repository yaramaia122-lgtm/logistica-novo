import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.warning("Por favor, faça login primeiro."); st.stop()

st.set_page_config(page_title="Agenda - AURA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header {
        background-color: #FF7F50 !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .trecho-header {
        background-color: #002D5E !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
</style>
""", unsafe_allow_html=True)

tk = st.secrets["GITHUB_TOKEN"]
rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])

f_v = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))
f_o = rp.get_contents("observacoes.csv")
df_o = pd.read_csv(io.StringIO(f_o.decoded_content.decode()))

# Observações Semanais Editáveis
st.markdown('<div class="agenda-header">OBSERVAÇÕES</div>', unsafe_allow_html=True)
obs_edit = st.data_editor(df_o, use_container_width=True, hide_index=True)
if st.button("💾 Salvar Observações"):
    rp.update_file("observacoes.csv", "Update", obs_edit.to_csv(index=False), f_o.sha)
    st.success("Salvo!"); st.rerun()

# Trecho 1: Pontes e Lacerda x Cuiabá
st.markdown('<br><div class="trecho-header">Pontes e Lacerda x Cuiabá</div>', unsafe_allow_html=True)
df_pl = df_v[df_v['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
cols_pl = ["Passageiro", "semana", "data", "horário", "saída", "Cia/nº voo", "Horário do Voo", "Data do Voo", "Hotel em Cuiabá", "Motorista"]
for c in cols_pl:
    if c not in df_pl.columns: df_pl[c] = ""
st.dataframe(df_pl[cols_pl], use_container_width=True, hide_index=True)

# Trecho 2: Cuiabá x Pontes e Lacerda
st.markdown('<br><div class="trecho-header">Cuiabá x Pontes e Lacerda</div>', unsafe_allow_html=True)
df_cp = df_v[df_v['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
cols_cp = ["Passageiro", "semana", "data", "horário", "Cia/nº voo", "Hotel Cuiabá", "semana_ret", "data_ret", "horário_ret", "Motorista", "Hospedagem . Lacerda"]
for c in cols_cp:
    if c not in df_cp.columns: df_cp[c] = ""
st.dataframe(df_cp[cols_cp], use_container_width=True, hide_index=True)
