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

def padronizar_data_br(txt):
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
    df_o.columns = df_o.columns.str.strip().str.lower()

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    
    # Padroniza as datas das observações para DD/MM/YYYY antes de mostrar na planilha
    if "data" in df_o.columns:
        df_o["data"] = df_o["data"].apply(padronizar_data_br)
        
    # Exibe as observações exatamente como o teu modelo de planilha interativa
    df_o_editada = st.data_editor(
        df_o[["dia", "data", "observacao"]],
        column_config={
            "dia": st.column_config.TextColumn("Dia da Semana", disabled=True, width="medium"),
            "data": st.column_config.TextColumn("Data", disabled=True, width="small"),
            "observacao": st.column_config.TextColumn("Observação", width="large")
        },
        hide_index=True,
        use_container_width=True,
        key="editor_obs"
    )

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = df_o_editada["observacao"]
        rp.update_file("observacoes.csv", "Update Obs Table", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Observações atualizadas com sucesso!"); st.rerun()

    st.markdown("---")
    lista_p = sorted([p for p in df_v["passageiro"].unique() if str(p).strip() != ""]) if "passageiro" in df_v.columns else []
    p_sel = st.multiselect("Filtrar por Passageiro:", options=lista_p)
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # Mapeamento rigoroso das despesas e colunas conforme as tuas imagens originais
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "hotel cuiabá", "semana.1", "data.1", "horário.1", "motorista", "hospedagem . lacerda"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    for c in list(set(cols_pl + cols_cp + cols_out)):
        if c not in df_f.columns: df_f[c] = ""
        else: df_f[c] = df_f[c].fillna("").astype(str).str.strip()

    # Força a formatação de todas as colunas que contenham datas para o padrão BR
    for c in df_f.columns:
        if "data" in c: df_f[c] = df_f[c].apply(padronizar_data_br)

    df_f["trajeto"] = df_f["trajeto"].str.lower()

    df_pl_r = df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"][cols_pl]
    df_cp_r = df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"][cols_cp]
    df_out_r = df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])][cols_out]

    # 📄 SEU BOTÃO DE DOWNLOAD DO RELATÓRIO DO MOTORISTA RECONSTITUÍDO
    html_res = f"""
    <html><head><meta charset='utf-8'></head><body>
    <h2>AURA APOENA LOGISTICS - AGENDA</h2>
    <h3>OBSERVAÇÕES DA SEMANA</h3>{df_o_editada.to_html(index=False, border=1)}
    <h3>PONTES E LACERDA X CUIABÁ</h3>{df_pl_r.to_html(index=False, border=1)}
    <h3>CUIABÁ X PONTES E LACERDA</h3>{df_cp_r.to_html(index=False, border=1)}
    </body></html>
    """
    st.download_button(label="📄 Baixar Relatório da Agenda (HTML/PDF)", data=html_res, file_name="agenda_aura.html", mime="text/html", width='stretch')

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_pl_r, width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_
