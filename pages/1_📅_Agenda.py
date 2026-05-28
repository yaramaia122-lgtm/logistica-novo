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

# 🛡️ PROTEÇÃO CONTRA KEYERROR: Verifica se as chaves existem nos Secrets antes de travar
if "GITHUB_TOKEN" not in st.secrets or "GITHUB_REPO" not in st.secrets:
    st.error("⚠️ Configuração incompleta: O GITHUB_TOKEN ou GITHUB_REPO não foi encontrado nos Secrets do Streamlit.")
    st.stop()

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    f_v = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))
    f_o = rp.get_contents("observacoes.csv")
    df_o = pd.read_csv(io.StringIO(f_o.decoded_content.decode()))

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    if df_o.empty:
        dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
        df_o = pd.DataFrame({"Data": dias_v, "Observacao": [""]*7})

    obs_edit = st.data_editor(df_o, use_container_width=True, hide_index=True)
    if st.button("💾 Salvar Observações"):
        rp.update_file("observacoes.csv", "Update", obs_edit.to_csv(index=False), f_o.sha)
        st.success("Salvo com sucesso!"); st.rerun()

    # Trecho 1
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_v[df_v['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
    cols_pl = ["Passageiro", "semana", "data", "horário", "saída", "Cia/nº voo", "Horário do Voo", "Data do Voo", "Hotel em Cuiabá", "Motorista"]
    for c in cols_pl:
        if c not in df_pl.columns: df_pl[c] = ""
    st.dataframe(df_pl[cols_pl], use_container_width=True, hide_index=True)

    # Trecho 2
    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_v[df_v['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
    cols_cp = ["Passageiro", "semana", "data", "horário", "Cia/nº voo", "Hotel Cuiabá", "semana_ret", "data_ret", "horário_ret", "Motorista", "Hospedagem . Lacerda"]
    for c in cols_cp:
        if c not in df_cp.columns: df_cp[c] = ""
    st.dataframe(df_cp[cols_cp], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro ao conectar com as planilhas do GitHub: {e}")
