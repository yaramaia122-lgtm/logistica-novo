import streamlit as st
import pandas as pd
from github import Github, Auth
import io
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
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
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

    # Tratamento Avançado de Conversão (Sanitização Absoluta de Colunas vindas da Programação)
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    # Mapeamento e normalização dos dados textuais para evitar quebras por valores nulos
    for col in df_v.columns:
        df_v[col] = df_v[col].fillna("").astype(str).str.strip()

    # Criação das colunas obrigatórias caso falte alguma na tabela de origem (Garantia de Conversão)
    colunas_obrigatorias = ["passageiro", "trajeto", "semana", "data", "horário", "saída", "motorista"]
    for col in colunas_obrigatorias:
        if col not in df_v.columns:
            df_v[col] = ""

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
        st.success("Observações atualizadas!"); st.rerun()

    st.markdown("---")
    st.write("### 🔍 Filtrar Programação por Passageiros")
    
    lista_passageiros = sorted([p for p in df_v["passageiro"].unique() if p != ""])
    passageiros_selecionados = st.multiselect("Selecione os passageiros (Vazio exibe todos):", options=lista_passageiros)

    df_filtrado = df_v[df_v['passageiro'].isin(passageiros_selecionados)] if passageiros_selecionados else df_v

    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "motorista"]
    cols_outros = ["passageiro", "trajeto", "semana", "data", "horário", "motorista"]

    # Divisão segura de exibições baseada nas strings convertidas da aba Programar
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_filtrado[df_filtrado['trajeto'].str.lower() == "pontes e lacerda x cuiabá"]
    st.dataframe(df_pl[cols_pl], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_filtrado[df_filtrado['trajeto'].str.lower() == "cuiabá x pontes e lacerda"]
    st.dataframe(df_cp[cols_cp], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros = df_filtrado[~df_filtrado['trajeto'].str.lower().isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])]
    st.dataframe(df_outros[cols_outros], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro na consistência de dados: {e}")
