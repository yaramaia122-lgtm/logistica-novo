import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

# 1. VERIFICAÇÃO DE LOGIN
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.switch_page("main.py")

st.set_page_config(page_title="Painel AURA", layout="wide")

# 2. CONEXÃO GITHUB
try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    f_log = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))
    # Normalizar nomes das colunas: remove espaços e coloca em minúsculas
    df_v.columns = df_v.columns.str.strip().str.lower()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    df_v = pd.DataFrame()

# 3. INTERFACE DE SELEÇÃO
st.subheader("Gestão de Registos")

if not df_v.empty:
    # Criar lista de seleção com base no que existe no ficheiro
    opcoes = ["➕ CRIAR NOVO"]
    for i, row in df_v.iterrows():
        # Tenta encontrar o nome do passageiro, se não houver, usa 'Sem Nome'
        nome = row.get('passageiro', 'Sem Nome')
        opcoes.append(f"{i} - {nome}")
    
    selecao = st.selectbox("Selecione para editar ou criar:", opcoes)
    
    # Lógica de Edição (Simplificada para evitar erros)
    idx = None
    if selecao != "➕ CRIAR NOVO":
        idx = int(selecao.split(" - ")[0])
    
    with st.form("form_registo"):
        # Campos básicos
        in_pass = st.text_input("Passageiro", value=df_v.at[idx, 'passageiro'] if idx is not None else "")
        in_mot = st.text_input("Motorista", value=df_v.at[idx, 'motorista'] if idx is not None else "")
        
        submitted = st.form_submit_button("Gravar Alterações")
        
        if submitted:
            nova_linha = {"passageiro": in_pass, "motorista": in_mot}
            
            if idx is None:
                # Adicionar linha
                df_v = pd.concat([df_v, pd.DataFrame([nova_linha])], ignore_index=True)
            else:
                # Atualizar linha existente
                for k, v in nova_linha.items():
                    df_v.at[idx, k] = v
            
            # Salvar no GitHub
            rp.update_file("dados_logistica.csv", "Update via Painel", df_v.to_csv(index=False), f_log.sha)
            st.success("Dados gravados com sucesso!")
            st.rerun()
else:
    st.warning("O ficheiro está vazio ou não pôde ser lido.")
    if st.button("Criar novo ficheiro com estrutura base"):
        df_base = pd.DataFrame(columns=['passageiro', 'motorista', 'data', 'trajeto', 'status'])
        rp.create_file("dados_logistica.csv", "Inicialização", df_base.to_csv(index=False))
        st.rerun()

st.dataframe(df_v)
