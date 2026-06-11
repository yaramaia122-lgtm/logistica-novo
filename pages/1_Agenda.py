import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 8px 12px; font-weight: bold; border-radius: 4px; margin-top: 15px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

def buscar_coluna_case_insensitive(df, nome_esperado):
    for col in df.columns:
        if str(col).strip().lower() == str(nome_esperado).lower():
            return col
    return None

def calcular_dia_semana(data_str):
    if not data_str or pd.isna(data_str) or str(data_str).strip() == "":
        return ""
    dias_traduzidos = {
        0: "Segunda-Feira", 1: "Terça-Feira", 2: "Quarta-Feira",
        3: "Quinta-Feira", 4: "Sexta-Feira", 5: "Sábado", 6: "Domingo"
    }
    try:
        data_str = str(data_str).strip()
        if len(data_str.split('/')) == 2:
            ano_atual = datetime.now().year
            dt_obj = datetime.strptime(f"{data_str}/{ano_atual}", "%d/%m/%Y")
        else:
            dt_obj = datetime.strptime(data_str, "%d/%m/%Y")
        return dias_traduzidos[dt_obj.weekday()]
    except:
        return ""

def limpar_e_garantir(df_alvo, colunas_alvo):
    df_temp = pd.DataFrame()
    for col in colunas_alvo:
        match_col = buscar_coluna_case_insensitive(df_alvo, col)
        if match_col:
            df_temp[col] = df_alvo[match_col].fillna("").astype(str).str.strip()
        else:
            df_temp[col] = ""
            
    if "semana" in df_temp.columns and "data" in df_temp.columns:
        mask_vazio = df_temp["semana"] == ""
        if mask_vazio.any():
            df_temp.loc[mask_vazio, "semana"] = df_temp.loc[mask_vazio, "data"].apply(calcular_dia_semana)
            
    return df_temp[colunas_alvo]

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    # Tratamento contra duplicados e padronização na leitura inicial
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    # Mapeamento flexível de colunas das observações para corrigir as datas em branco
    col_obs_dia = buscar_coluna_case_insensitive(df_o, "dia") or "dia"
    col_obs_data = buscar_coluna_case_insensitive(df_o, "data") or "data"
    col_obs_texto = buscar_coluna_case_insensitive(df_o, "observacao") or "observacao"

    st.markdown('<div class="agenda-header">📋 OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for idx, row in df_o.iterrows():
        c1, c2, c3 = st.columns([1.5, 1, 6.5])
        
        # Resgate seguro dos valores reais salvos na sua planilha de observações
        val_dia = row.get(col_obs_dia, "")
        val_data = row.get(col_obs_data, "")
        val_txt = row.get(col_obs_texto, "")
        
        c1.markdown(f"<p style='padding-top:15px; font-weight:bold;'>{str(val_dia) if pd.notna(val_dia) else ''}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='padding-top:15px; color:#555555;'>{str(val_data) if pd.notna(val_data) else ''}</p>", unsafe_allow_html=True)
        novas_obs.append(c3.text_area(label=f"O_{idx}", value=str(val_txt) if pd.notna(val_txt
