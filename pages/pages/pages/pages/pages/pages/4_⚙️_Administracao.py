import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.stop()

st.set_page_config(page_title="Administração - AURA", layout="wide")

tk = st.secrets["GITHUB_TOKEN"]
rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])

f_v = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))

f_u = rp.get_contents("usuarios.csv")
df_u = pd.read_csv(io.StringIO(f_u.decoded_content.decode()))

tab1, tab2 = st.tabs(["💰 Histórico Completo de Custos", "👤 Gestão Avançada de Usuários"])

with tab1:
    st.write("Abaixo você gerencia todos os custos vinculados aos Centros de Custo:")
    ed_f = st.data_editor(df_v, use_container_width=True, hide_index=True)
    if st.button("Salvar Custos"):
        rp.update_file("dados_logistica.csv", "Edit Fin", ed_f.to_csv(index=False), f_v.sha)
        st.success("Planilha financeira atualizada!"); st.rerun()

with tab2:
    st.write("Controle corporativo de acessos (Criação, Reset e Redefinição de Senhas)")
    ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
    if st.button("Salvar Usuários e Permissões"):
        rp.update_file("usuarios.csv", "Edit Users", ed_u.to_csv(index=False), f_u.sha)
        st.success("Base de dados de usuários salva!"); st.rerun()
