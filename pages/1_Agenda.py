import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime
import zoneinfo

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False; st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; border-radius: 4px; margin-top: 12px; }
</style>""", unsafe_allow_html=True)

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_o.columns = df_o.columns.str.strip().str.lower()
    df_v.columns = df_v.columns.str.strip().str.lower()
    
    df_o = df_o.loc[:, ~df_o.columns.duplicated()]
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    
    for c in ["dia", "data", "observacao"]: df_o[c] = df_o[c].fillna("").astype(str).str.strip() if c in df_o.columns else ""

    st.markdown('<div class="agenda-header">Observações</div>', unsafe_allow_html=True)
    df_o_edit = st.data_editor(df_o[["dia", "data", "observacao"]], column_config={"dia": st.column_config.TextColumn("Dia da Semana", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "observacao": st.column_config.TextColumn("Observação", width="large")}, hide_index=True, width='stretch', row_height=100, key="ed_obs_v16")

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = df_o_edit["observacao"]
        rp.update_file("observacoes.csv", "Update", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    
    lista_p = sorted([p for p in df_v["passageiro"].unique() if str(p).strip() != ""]) if "passageiro" in df_v.columns else []
    p_sel = st.multiselect("Filtrar por Passageiro:", options=lista_p)
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # Listas oficiais de exibição de colunas
    c_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "motorista"]
    c_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "horário do voo", "hotel cuiabá", "semana.1", "data.1", "horário.1", "hospedagem . lacerda", "motorista"]
    c_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    df_f_limpo = df_f.fillna("").astype(str)

    # 🛡️ NORMALIZAÇÃO ANTIFALHAS: Remove acentos e espaços para garantir o filtro correto dos trechos
    t_normalizado = df_f_limpo['trajeto'].str.strip().str.lower().str.replace("á", "a")
    
    df_pl_r = df_f_limpo[t_normalizado == "pontes e lacerda x cuiaba"][[c for c in c_pl if c in df_f_limpo.columns]]
    df_cp_r = df_f_limpo[t_normalizado == "cuiaba x pontes e lacerda"][[c for c in c_cp if c in df_f_limpo.columns]]
    df_out_r = df_f_limpo[(t_normalizado != "pontes e lacerda x cuiaba") & (t_normalizado != "cuiaba x pontes e lacerda")][[c for c in c_out if c in df_f_limpo.columns]]

    dt_c = datetime.now(zoneinfo.ZoneInfo("America/Cuiaba")).strftime('%d/%m/%Y às %H:%M')
    df_o_html = df_o_edit.copy()
    df_o_html["observacao"] = df_o_html["observacao"].astype(str).str.replace("\n", "<br>")

    style_t = "<style>body{font-family:Arial;font-size:10px;} .m{text-align:right;color:#555;} h2{background:#FF7F50;color:white;text-align:center;padding:5px;} h3{background:#002D5E;color:white;padding:4px;} table{width:100%;border-collapse:collapse;margin-bottom:10px;} th,td{border:1px solid #ddd;padding:4px;vertical-align:top;} th{background:#f2f2f2;}</style>"
    html_out = f"<html><head><meta charset='utf-8'>{style_t}</head><body><div class='m'>Emitido em: {dt_c}</div><h2>AURA LOGISTICS</h2><h3>OBSERVAÇÕES</h3>{df_o_html.to_html(index=False, escape=False)}<h3>P. LACERDA X CUIABÁ</h3>{df_pl_r.to_html(index=False)}<h3>CUIABÁ X P. LACERDA</h3>{df_cp_r.to_html(index=False)}</body></html>"
    st.download_button(label="📄 Baixar Relatório Otimizado (HTML/PDF 1 Página)", data=html_out, file_name="agenda_1_pagina.html", mime="text/html", width='stretch')

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_pl_r, width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_cp_r, width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_out_r, width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
