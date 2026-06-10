import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']: st.stop()

st.set_page_config(page_title="Administração - AURA", layout="wide")

tk = st.secrets["GITHUB_TOKEN"]
rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])

f_v = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))

tab1, tab2 = st.tabs(["Registro Completo de Custos", "Configurações de Sistema"])

with tab1:
    st.write("Edite as informações financeiras e trajetos salvos na base:")
    ed_f = st.data_editor(df_v, use_container_width=True, hide_index=True)
    if st.button("Salvar Modificações de Custos"):
        rp.update_file("dados_logistica.csv", "Edit Fin", ed_f.to_csv(index=False), f_v.sha)
        st.success("Histórico financeiro atualizado com sucesso."); st.rerun()

with tab2:
    st.write("Configurações gerais de administração de dados.")
    st.info("O banco de dados de usuários está operando localmente na memória do sistema para máxima segurança.")
