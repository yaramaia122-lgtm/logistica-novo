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

def ajustar_data_br(txt):
    if not txt or pd.isna(txt) or str(txt).strip() == "" or str(txt).lower() == "nan": return ""
    t = str(txt).strip().split(" ")[0]
    try:
        if "-" in t: return datetime.strptime(t, "%Y-%m-%d").strftime("%d/%m/%Y")
        p = t.split("/")
        if len(p) == 2: return datetime.strptime(f"{t}/{datetime.now().year}", "%d/%m/%Y").strftime("%d/%m/%Y")
        if len(p) == 3:
            if len(p[2]) == 2: p[2] = "20" + p[2]
            return datetime.strptime("/".join(p), "%d/%m/%Y").strftime("%d/%m/%Y")
    except: return t
    return t

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    
    # Montagem do cabeçalho da planilha de observações
    c_head1, c_head2, c_head3 = st.columns([2, 2, 6])
    c_head1.markdown("**Dia da Semana**")
    c_head2.markdown("**Data**")
    c_head3.markdown("**Observação**")
    st.markdown("---")

    novas_obs = []
    for idx, row in df_o.iterrows():
        c1, c2, c3 = st.columns([2, 2, 6])
        v_data = ajustar_data_br(row.get('data', ''))
        v_dia = str(row.get('dia', '')).strip()
        
        c1.markdown(f"<p style='padding-top:10px;'>{v_dia}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='padding-top:10px; color:#555555;'>{v_data}</p>", unsafe_allow_html=True)
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
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "horário do voo", "hotel cuiabá", "hospedagem . lacerda", "motorista"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    for c in list(set(cols_pl + cols_cp + cols_out)):
        if c not in df_f.columns: df_f[c] = ""
        else: df_f[c] = df_f[c].fillna("").astype(str).str.strip()

    for c in df_f.columns:
        if "data" in c: df_f[c] = df_f[c].apply(ajustar_data_br)

    df_f["trajeto"] = df_f["trajeto"].str.lower()

    df_pl_r = df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"][cols_pl]
    df_cp_r = df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"][cols_cp]
    df_out_r = df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])][cols_out]

    html_res = f"<html><body><h2>AURA LOGISTICS</h2><h3>PONTES E LACERDA X CUIABÁ</h3>{df_pl_r.to_html(index=False, border=1)}<h3>CUIABÁ X PONTES E LACERDA</h3>{df_cp_r.to_html(index=False, border=1)}</body></html>"
    st.download_button(label="📄 Baixar Relatório da Agenda (HTML/PDF)", data=html_res, file_name="agenda.html", mime="text/html", width='stretch')

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_pl_r, width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_cp_r, width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_out_r, width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
