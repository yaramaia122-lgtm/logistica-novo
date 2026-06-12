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

    df_v.columns, df_o.columns = df_v.columns.str.strip().str.lower(), df_o.columns.str.strip().str.lower()
    df_v, df_o = df_v.loc[:, ~df_v.columns.duplicated()], df_o.loc[:, ~df_o.columns.duplicated()]

    st.markdown('<div class="agenda-header">Observações</div>', unsafe_allow_html=True)
    df_o_edit = st.data_editor(df_o[["dia", "data", "observacao"]], column_config={"dia": st.column_config.TextColumn("Dia da Semana", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "observacao": st.column_config.TextColumn("Observação", width="large")}, hide_index=True, width='stretch', row_height=100, key="ed_obs_v13")

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = df_o_edit["observacao"]
        rp.update_file("observacoes.csv", "Update", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    p_sel = st.multiselect("Filtrar por Passageiro:", options=sorted(list(df_v["passageiro"].dropna().unique())))
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # 🛡️ OCULTA OS CUSTOS DA TELA AUTOMATICAMENTE
    cols = [c for c in df_f.columns if "r$" not in c and "custo" not in c and "trajeto" not in c]
    df_limpo = df_f[cols].fillna("").astype(str)

    # Filtros simplificados em variáveis curtas para evitar o corte do arquivo
    t_str = df_f['trajeto'].astype(str).str.strip().str.lower()
    df_pl = df_limpo[t_str == "pontes e lacerda x cuiabá"]
    df_cp = df_limpo[t_str == "cuiabá x pontes e lacerda"]
    df_out = df_limpo[(t_str != "pontes e lacerda x cuiabá") & (t_str != "cuiabá x pontes e lacerda")]

    dt_c = datetime.now(zoneinfo.ZoneInfo("America/Cuiaba")).strftime('%d/%m/%Y às %H:%M')
    style_t = "<style>body{font-family:Arial;font-size:10px;} .m{text-align:right;color:#555;} h2{background:#FF7F50;color:white;text-align:center;padding:5px;} h3{background:#002D5E;color:white;padding:4px;} table{width:100%;border-collapse:collapse;margin-bottom:10px;} th,td{border:1px solid #ddd;padding:4px;vertical-align:top;} th{background:#f2f2f2;}</style>"
    html_out = f"<html><head><meta charset='utf-8'>{style_t}</head><body><div class='m'>Emitido em: {dt_c}</div><h2>AURA LOGISTICS</h2><h3>OBSERVAÇÕES</h3>{df_o_edit.to_html(index=False)}<h3>P. LACERDA X CUIABÁ</h3>{df_pl.to_html(index=False)}<h3>CUIABÁ X P. LACERDA</h3>{df_cp.to_html(index=False)}</body></html>"
    st.download_button(label="📄 Baixar Relatório Otimizado (HTML/PDF 1 Página)", data=html_out, file_name="agenda_1_pagina.html", mime="text/html", width='stretch')

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_pl.dropna(how='all', axis=1), width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_cp.dropna(how='all', axis=1), width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_out.dropna(how='all', axis=1), width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
