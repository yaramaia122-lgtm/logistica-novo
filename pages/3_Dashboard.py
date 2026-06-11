import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Dashboard - AURA", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.write(f"Usuário ativo: **{st.session_state.get('user', 'Funcionário')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['user'] = None
        st.switch_page("main.py")

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)
    f_v = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))

    df_v["Total"] = pd.to_numeric(df_v["Total"], errors="coerce").fillna(0)
    df_at = df_v[df_v["Status"] != "Cancelada"]

    st.write("### Indicadores Operacionais e Financeiros")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Viagens Agendadas", len(df_at))
    m2.metric("Quantidade de Passageiros", df_at["Passageiro"].nunique())
    m3.metric("Valores Totais Ativos", f"R$ {df_at['Total'].sum():,.2f}")
    m4.metric("Motoristas Alocados", df_at["Motorista"].nunique())

    st.markdown("---")
    st.write("### Custos Estruturados por Centro de Custo")
    if not df_at.empty:
        st.bar_chart(df_at.groupby("Centro_Custo")["Total"].sum())
    else:
        st.info("Nenhum dado de custo ativo encontrado para gerar os gráficos.")

except Exception as e:
    st.error(f"Erro na conexão com o banco de dados: {e}")
