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

st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA (Clique para editar)</div>', unsafe_allow_html=True)
obs_edit = st.data_editor(df_o, use_container_width=True, hide_index=True)
if st.button("💾 Salvar Alterações de Observações"):
    rp.update_file("observacoes.csv", "Update via Agenda", obs_edit.to_csv(index=False), f_o.sha)
    st.success("Observações salvas!"); st.rerun()

st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
df_pl = df_v[df_v['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
st.dataframe(df_pl[["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]], use_container_width=True, hide_index=True)

st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
df_cp = df_v[df_v['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
st.dataframe(df_cp[["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Hospedagem", "Motorista"]], use_container_width=True, hide_index=True)
