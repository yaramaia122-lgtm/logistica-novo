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
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 8px 12px; font-weight: bold; border-radius: 4px; margin-top: 15px; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

def auto_calcular_semana(data_str):
    if not data_str or pd.isna(data_str) or str(data_str).strip() == "" or str(data_str).lower() == "nan":
        return ""
    dias = {0: "Segunda-Feira", 1: "Terça-Feira", 2: "Quarta-Feira", 3: "Quinta-Feira", 4: "Sexta-Feira", 5: "Sábado", 6: "Domingo"}
    try:
        ds = str(data_str).strip()
        if "-" in ds: ds = datetime.strptime(ds.split(" ")[0], "%Y-%m-%d").strftime("%d/%m/%Y")
        p = ds.split("/")
        dt = datetime.strptime(f"{ds}/{datetime.now().year}" if len(p)==2 else ds, "%d/%m/%Y")
        return dias[dt.weekday()]
    except: return ""

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    st.markdown('<div class="agenda-header">📋 OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for idx, row in df_o.iterrows():
        c1, c2, c3 = st.columns([1.5, 1, 6.5])
        v_data = str(row.get('data', '')).strip() if pd.notna(row.get('data', '')) else ""
        v_dia = str(row.get('dia', '')).strip() if pd.notna(row.get('dia', '')) else ""
        if (v_dia == "" or v_dia == "nan") and v_data != "": v_dia = auto_calcular_semana(v_data)
        
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

    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "hotel cuiabá", "motorista", "hospedagem . lacerda"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    for c in list(set(cols_pl + cols_cp + cols_out)):
        if c not in df_f.columns: df_f[c] = ""
        else: df_f[c] = df_f[c].fillna("").astype(str).str.strip()

    # 🛡️ PROTEÇÃO ATIVA: Se dados antigos vierem sem semana, calcula dinamicamente para não exibir em branco
    if "semana" in df_f.columns and "data" in df_f.columns:
        for i, r in df_f.iterrows():
            if r["semana"] == "" or r["semana"] == "nan":
                df_f.at[i, "semana"] = auto_calcular_semana(r["data"])

    df_f["trajeto"] = df_f["trajeto"].str.lower()

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"][cols_pl], width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"][cols_cp], width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])][cols_out], width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
