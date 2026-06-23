import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Dashboard - AURA LOGISTICS", layout="wide")

# 🎨 ESTILIZAÇÃO CORPORATIVA PROFISSIONAL
st.markdown("""<style>
    .stApp { background-color: #F8FAFC !important; }
    .main-title { color: #002D5E !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
    .subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }
    .section-header { background-color: #002D5E !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Painel de Controle de Custos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Análise financeira consolidada, rateio de despesas operacionais e balanço geral</div>', unsafe_allow_html=True)

tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
df_v.columns = df_v.columns.str.strip().str.lower()

# Conversão limpa para dados numéricos reais
for col in ["hotel_v", "comb_v", "aereo_v", "outros_v", "total", "hotel (r$)", "aéreo (r$)", "transfer (r$)", "outros (r$)"]:
    if col in df_v.columns:
        df_v[col] = pd.to_numeric(df_v[col].astype(str).str.replace("R$", "").str.replace(",", ".").str.strip(), errors='coerce').fillna(0.0)

tot_hotel = df_v["hotel_v"].sum() if "hotel_v" in df_v.columns else df_v["hotel (r$)"].sum()
tot_aereo = df_v["aereo_v"].sum() if "aereo_v" in df_v.columns else df_v["aéreo (r$)"].sum()
tot_comb = df_v["comb_v"].sum() if "comb_v" in df_v.columns else df_v["transfer (r$)"].sum()
tot_outros = df_v["outros_v"].sum() if "outros_v" in df_v.columns else df_v["outros (r$)"].sum()

custo_total_geral = tot_hotel + tot_aereo + tot_comb + tot_outros

st.write("### Consolidação por Centro de Custo")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Hospedagens", f"R$ {tot_hotel:,.2f}")
c2.metric("Passagens Aéreas", f"R$ {tot_aereo:,.2f}")
c3.metric("Deslocamento / Transfer", f"R$ {tot_comb:,.2f}")
c4.metric("Despesas Diversas", f"R$ {tot_outros:,.2f}")

st.markdown("---")
st.metric("CUSTO TOTAL ACUMULADO DA OPERAÇÃO", f"R$ {custo_total_geral:,.2f}")

st.markdown('<div class="section-header">Histórico Financeiro Analítico</div>', unsafe_allow_html=True)
st.dataframe(df_v, width='stretch', hide_index=True)
