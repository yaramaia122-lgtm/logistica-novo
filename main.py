import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import streamlit.components.v1 as components
from datetime import datetime, timedelta

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.write(f"Usuário ativo: **{st.session_state.get('user', 'Funcionário')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['user'] = None
        st.switch_page("main.py")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header {
        background-color: #FF7F50 !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
        margin-bottom: 0px;
    }
    .trecho-header {
        background-color: #002D5E !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: sans-serif !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    f_v = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))
    
    f_o = rp.get_contents("observacoes.csv")
    df_o = pd.read_csv(io.StringIO(f_o.decoded_content.decode()))

    # Padronização de segurança para os nomes das colunas
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    if "passageiro" in df_v.columns:
        df_v["passageiro"] = df_v["passageiro"].fillna("").astype(str)
    else:
        df_v["passageiro"] = ""

    if "trajeto" in df_v.columns:
        df_v["trajeto"] = df_v["trajeto"].fillna("").astype(str)
    else:
        df_v["trajeto"] = ""

    dias_semana_nome = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    
    if "dia" not in df_o.columns or df_o.empty or len(df_o) < 7:
        dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        textos_antigos = df_o["observacao"].tolist() if "observacao" in df_o.columns else [""]*7
        if len(textos_antigos) < 7: textos_antigos += [""] * (7 - len(textos_antigos))
        df_o = pd.DataFrame({"dia": dias_semana_nome, "data": dias_v, "observacao": textos_antigos[:7]})
    
    df_o["observacao"] = df_o["observacao"].fillna("").astype(str)

    # Painel de Observações
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        with c_dia:
            st.markdown(f"<p style='padding-top:15px; font-weight:bold; color:#333333;'>{row['dia']}</p>", unsafe_allow_html=True)
        with c_data:
            st.markdown(f"<p style='padding-top:15px; color:#555555;'>{row['data']}</p>", unsafe_allow_html=True)
        with c_texto:
            texto_inserido = st.text_area(label=f"Obs {row['dia']}", value=row['observacao'], key=f"obs_{index}", label_visibility="collapsed")
            novas_obs.append(texto_inserido)
        st.markdown("<hr style='margin: 0px 0px 5px 0px; border-color:#E0E0E0;'>", unsafe_allow_html=True)

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["observacao"] = novas_obs
        df_o.columns = ["dia", "data", "observacao"]
        rp.update_file("observacoes.csv", "Update Observacoes", df_o.to_csv(index=False), f_o.sha)
        st.success("Observações sincronizadas com sucesso."); st.rerun()

    st.markdown("---")
    
    # Filtro Multi-Seleção Avançado
    st.write("### 🔍 Filtrar Programação por Passageiros")
    lista_passageiros = sorted(
