import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# 1. VALIDAÇÃO DE ACESSO
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide", initial_sidebar_state="expanded")

# 2. BARRA LATERAL
with st.sidebar:
    st.write(f"Usuário ativo: **{st.session_state.get('user', 'Funcionário')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['user'] = None
        st.switch_page("main.py")

# Estilos Visuais da Agenda
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
</style>
""", unsafe_allow_html=True)

try:
    # 3. CONEXÃO COM REPOSITÓRIO
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    f_v = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))
    
    f_o = rp.get_contents("observacoes.csv")
    df_o = pd.read_csv(io.StringIO(f_o.decoded_content.decode()))

    # 4. SANITIZAÇÃO E CONVERSÃO DOS DADOS DA PROGRAMAÇÃO
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    # Normalizar valores nulos para evitar quebras de conversão de string
    for col in df_v.columns:
        df_v[col] = df_v[col].fillna("").astype(str).str.strip()

    # FUNÇÃO CRÍTICA: Garante que o DataFrame tenha as colunas necessárias para exibição
    def garantir_colunas_existentes(df_origem, colunas_desejadas):
        df_copia = df_origem.copy()
        for col in colunas_desejadas:
            if col not in df_copia.columns:
                df_copia[col] = ""  # Cria a coluna vazia se ela não veio da aba Programar
        return df_copia[colunas_desejadas]

    # 5. QUADRO DE OBSERVAÇÕES
    dias_semana_nome = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    if "dia" not in df_o.columns or df_o.empty:
        dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        df_o = pd.DataFrame({"dia": dias_semana_nome, "data": dias_v, "observacao": [""]*7})
    
    df_o["observacao"] = df_o["observacao"].fillna("").astype(str)

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        with c_dia: st.markdown(f"<p style='padding-top:15px; font-weight:bold;'>{row['dia']}</p>", unsafe_allow_html=True)
        with c_data: st.markdown(f"<p style='padding-top:15px; color:#555555;'>{row['data']}</p>", unsafe_allow_html=True)
        with c_texto:
            t = st.text_area(label=f"Obs_{index}", value=row['observacao'], key=f"obs_{index}", label_visibility="collapsed")
            novas_obs.append(t)

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Observacoes", df_o.to_csv(index=False), f_o.sha)
        st.success("Observações atualizadas com sucesso!")
        st.rerun()

    st.markdown("---")
    
    # 6. FILTRO DE PASSAGEIROS
    st.write("### 🔍 Filtrar Programação por Passageiros")
    lista_passageiros = sorted([p for p in df_v["passageiro"].unique() if p != ""]) if "passageiro" in df_v.columns else []
    passageiros_selecionados = st.multiselect("Selecione os passageiros (Vazio exibe todos):", options=lista_passageiros)

    df_filtrado = df_v[df_v['passageiro'].isin(passageiros_selecionados)] if passageiros_selecionados else df_v

    # Definição das colunas de exibição por bloco
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "motorista"]
    cols_outros = ["passageiro", "trajeto", "semana", "data", "horário", "motorista"]

    # 7. RENDERIZAÇÃO SEGURA DAS TABELAS (SEM RISCO DE KEYERROR)
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl_screen = df_filtrado[df_filtrado['trajeto'].str.lower() == "pontes e lacerda x cuiabá"]
    df_pl_render = garantir_colunas_existentes(df_pl_screen, cols_pl)
    st.dataframe(df_pl_render, use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp_screen = df_filtrado[df_filtrado['trajeto'].str.lower() == "cuiabá x pontes e lacerda"]
    df_cp_render = garantir_colunas_existentes(df_cp_screen, cols_cp)
    st.dataframe(df_cp_render, use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros_screen = df_filtrado[~df_filtrado['trajeto'].str.lower().isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])]
    df_outros_render = garantir_colunas_existentes(df_outros_screen, cols_outros)
    st.dataframe(df_outros_render, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro na consistência ou conversão de dados: {e}")
