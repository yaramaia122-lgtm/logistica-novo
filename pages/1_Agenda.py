import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 8px 12px; font-weight: bold; border-radius: 4px; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))

    # Limpeza bruta de colunas duplicadas
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    # Colunas exatas que o motorista precisa ver (conforme as tabelas originais)
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "hotel cuiabá", "motorista", "hospedagem . lacerda"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    # Garante que nenhuma coluna das listas falte no DataFrame
    for c in list(set(cols_pl + cols_cp + cols_out)):
        if c not in df_v.columns: df_v[c] = ""
        else: df_v[c] = df_v[c].fillna("").astype(str).str.strip()

    df_v["trajeto"] = df_v["trajeto"].str.lower()
    
    st.write("### 🔍 Filtrar por Passageiros")
    p_sel = st.multiselect("Selecione:", options=sorted([p for p in df_v["passageiro"].unique() if p != ""]))
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"][cols_pl], use_container_width=True, hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"][cols_cp], use_container_width=True, hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])][cols_out], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
