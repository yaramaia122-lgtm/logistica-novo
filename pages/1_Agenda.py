import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

with st.sidebar:
    st.write(f"Usuário: **{st.session_state.get('user', 'Funcionário')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.switch_page("main.py")

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    
    # Padronização e remoção de duplicados na leitura
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    # Mapeamento exato das colunas que o motorista precisa ver
    cols = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "motorista"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    # Força a criação limpa de colunas caso faltem no banco
    for col in cols_out:
        if col not in df_v.columns: df_v[col] = ""
        else: df_v[col] = df_v[col].fillna("").astype(str).str.strip()

    df_v["trajeto"] = df_v["trajeto"].str.lower()

    st.title("📋 Agenda de Logística - AURA")
    
    lista_p = sorted([p for p in df_v["passageiro"].unique() if p != ""])
    p_sel = st.multiselect("Filtrar por Passageiro:", options=lista_p)
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # Relatório nativo gerado direto pelo Pandas sem risco de aspas
    html_res = f"<html><body><h2>AURA LOGISTICS</h2>{df_f[cols_out].to_html(index=False, border=1)}</body></html>"
    st.download_button(label="📄 Baixar Relatório da Agenda (HTML)", data=html_res, file_name="agenda.html", mime="text/html", use_container_width=True)

    st.write("---")
    st.subheader("✈️ PONTES E LACERDA X CUIABÁ")
    st.dataframe(df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"][cols], use_container_width=True, hide_index=True)

    st.subheader("✈️ CUIABÁ X PONTES E LACERDA")
    st.dataframe(df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"][cols], use_container_width=True, hide_index=True)

    st.subheader("🚗 OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)")
    st.dataframe(df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])][cols_out], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
