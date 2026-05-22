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

tab1, tab2 = st.tabs(["💰 Registro e Edição de Custos", "👤 Controle e Reset de Usuários"])

with tab1:
    st.write("Edite os lançamentos financeiros diretamente na tabela:")
    ed_f = st.data_editor(df_v, use_container_width=True, hide_index=True)
    if st.button("Salvar Modificações de Custos"):
        rp.update_file("dados_logistica.csv", "Edit Fin", ed_f.to_csv(index=False), f_v.sha)
        st.success("Base de custos atualizada!"); st.rerun()

with tab2:
    st.write("Criação de acessos corporativos e gerenciamento de senhas padronizadas:")
    ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
    if st.button("Confirmar Alterações de Usuários"):
        rp.update_file("usuarios.csv", "Edit Users", ed_u.to_csv(index=False), f_u.sha)
        st.success("Tabela de acessos sincronizada!"); st.rerun()
