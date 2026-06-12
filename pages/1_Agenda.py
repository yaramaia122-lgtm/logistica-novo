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
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

def converter_data_br(dt_val):
    if not dt_val or pd.isna(dt_val) or str(dt_val).strip() == "" or str(dt_val).lower() == "nan":
        return ""
    s = str(dt_val).strip()
    if " " in s: s = s.split(" ")[0]
    try:
        if "-" in s:
            return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")
        p = s.split("/")
        if len(p) == 2:
            return datetime.strptime(f"{s}/{datetime.now().year}", "%d/%m/%Y").strftime("%d/%m/%Y")
        elif len(p) == 3:
            if len(p[2]) == 2: p[2] = "20" + p[2]
            return datetime.strptime("/".join(p), "%d/%m/%Y").strftime("%d/%m/%Y")
    except:
        return s
    return s

def calcular_dia_semana(dt_str):
    if not dt_str or pd.isna(dt_str) or str(dt_str).strip() == "":
        return ""
    dias = {0: "Segunda-Feira", 1: "Terça-Feira", 2: "Quarta-Feira", 3: "Quinta-Feira", 4: "Sexta-Feira", 5: "Sábado", 6: "Domingo"}
    try:
        clean_dt = converter_data_br(dt_str)
        return dias[datetime.strptime(clean_dt, "%d/%m/%Y").weekday()]
    except:
        return ""

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for idx, row in df_o.iterrows():
        c1, c2, c3 = st.columns([1.5, 1, 6.5])
        v_data = converter_data_br(row.get('data', ''))
        v_dia = row.get('dia', '')
        if (not v_dia or str(v_dia).strip() == "" or str(v_dia).lower() == "nan") and v_data != "":
            v_dia = calcular_dia_semana(v_data)
            
        c1.markdown(f"<p style='padding-top:15px; font-weight:bold;'>{v_dia}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='padding-top:15px; color:#555555;'>{v_data}</p>", unsafe_allow_html=True)
        novas_obs.append(c3.text_area(label=f"O_{idx}", value=str(row.get('observacao', '')), key=f"obs_{idx}", label_visibility="collapsed"))

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Obs", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    lista_p = sorted([p for p in df_v["passageiro"].unique() if str(p).strip() != ""]) if "passageiro" in df_v.columns else []
    p_sel = st.multiselect("Filtrar por Passageiro:", options=lista_p)
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # Suas colunas completas com custos devolvidas ao sistema
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "custo", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "horário do voo", "hotel cuiabá", "hospedagem . lacerda", "custo", "motorista"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "custo", "motorista"]

    for c in list(set(cols_pl + cols_cp + cols_out)):
        if c not in df_f.columns: df_f[c] = ""
        else: df_f[c] = df_f[c].fillna("").astype(str).str.strip()

    # Formata datas e reconstrói semanas vazias dos dados antigos
    for c in df_f.columns:
        if "data" in c: df_f[c] = df_f[c].apply(converter_data_
