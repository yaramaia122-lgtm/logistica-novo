import streamlit as st
import pandas as pd
from github import Github, Auth
import io

# Proteção de acesso direto via URL
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.set_page_config(page_title="Acesso Negado", layout="wide")
    st.warning("Por favor, realize o login para acessar esta página.")
    st.stop()

st.set_page_config(page_title="Administração - AURA", layout="wide", initial_sidebar_state="expanded")

# Menu Lateral Corporativo com Botão de Sair Formalizado
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

    f_u = rp.get_contents("usuarios.csv")
    df_u = pd.read_csv(io.StringIO(f_u.decoded_content.decode()))

    tab1, tab2 = st.tabs(["Registro Completo de Custos", "Gestão Corporativa de Usuários"])

    with tab1:
        st.write("Edite as informações financeiras e trajetos salvos na base:")
        ed_f = st.data_editor(df_v, use_container_width=True, hide_index=True)
        if st.button("Salvar Modificações de Custos"):
            rp.update_file("dados_logistica.csv", "Edit Fin", ed_f.to_csv(index=False), f_v.sha)
            st.success("Histórico financeiro atualizado com sucesso."); st.rerun()

    with tab2:
        st.write("Adicione novos usuários ou force a troca de senha preenchendo 'Sim' na coluna correspondente:")
        
        # O data_editor permite gerenciar os logins de forma visual direta na tela
        ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("Confirmar Alterações de Segurança"):
            rp.update_file("usuarios.csv", "Edit Users", ed_u.to_csv(index=False), f_u.sha)
            st.success("Configurações de acesso corporativo sincronizadas com sucesso!"); st.rerun()

except Exception as e:
    st.error(f"Erro ao carregar o módulo administrativo: {e}")
