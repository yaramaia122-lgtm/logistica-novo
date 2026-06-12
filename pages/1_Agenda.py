import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime
import zoneinfo

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False; st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; border-radius: 4px; margin-top: 12px; }
</style>""", unsafe_allow_html=True)

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns, df_o.columns = df_v.columns.str.strip().str.lower(), df_o.columns.str.strip().str.lower()
    df_v, df_o = df_v.loc[:, ~df_v.columns.duplicated()], df_o.loc[:, ~df_o.columns.duplicated()]

    st.markdown('<div class="agenda-header">Observações</div>', unsafe_allow_html=True)
    df_o_edit = st.data_editor(df_o[["dia", "data", "observacao"]], column_config={"dia": st.column_config.TextColumn("Dia da Semana", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "observacao": st.column_config.TextColumn("Observação", width="large")}, hide_index=True, width='stretch', row_height=100, key="ed_obs_v12")

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = df_o_edit["observacao"]
        rp.update_file("observacoes.csv", "Update", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    p_sel = st.multiselect("Filtrar por Passageiro:", options=sorted(list(df_v["passageiro"].dropna().unique())))
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # 🛡️ REMOÇÃO AUTOMÁTICA DE CUSTOS: Filtra e oculta as colunas financeiras da tela dinamicamente
    cols_visiveis = [c for c in df_f.columns if "r$" not in c and "custo" not in c and "trajeto" not in c]
    df_f_limpo = df_f[cols_visiveis].fillna("").astype(str)

    df_pl_r = df_f_limpo[df_f['trajeto'] == "pontes e lacerda x cuiabá"]
    df_cp_r = df_f_limpo[df_f['trajeto'] == "cuiabá x pontes e lacerda"]
    df_out_r = df_f_limpo[~df_f['trajeto'].isin(
