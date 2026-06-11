import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

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

# Seu estilo e visual original totalmente preservados
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 0px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-family: sans-serif !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    # Proteção contra colunas duplicadas e nulas
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    df_v["passageiro"] = df_v["passageiro"].fillna("").astype(str).str.strip() if "passageiro" in df_v.columns else ""
    df_v["trajeto"] = df_v["trajeto"].fillna("").astype(str).str.strip().str.lower() if "trajeto" in df_v.columns else ""

    def corrigir_colunas_faltantes(df_alvo, colunas_requisitadas):
        df_temp = df_alvo.copy()
        for col in colunas_requisitadas:
            if col not in df_temp.columns: df_temp[col] = ""
        return df_temp[colunas_requisitadas]

    # Painel de Observações
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        c_dia.markdown(f"<p style='padding-top:15px; font-weight:bold; color:#333333;'>{row.get('dia', '')}</p>", unsafe_allow_html=True)
        c_data.markdown(f"<p style='padding-top:15px; color:#555555;'>{row.get('data', '')}</p>", unsafe_allow_html=True)
        t_val = row.get('observacao', '')
        t = c_texto.text_area(label=f"Obs_{index}", value=t_val if pd.notna(t_val) else "", key=f"obs_{index}", label_visibility="collapsed")
        novas_obs.append(t)

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Obs", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Observações salvas!"); st.rerun()

    st.markdown("---")
    st.write("### 🔍 Filtrar Programação por Passageiros")
    lista_p = sorted([p for p in df_v["passageiro"].unique() if p != ""])
    p_sel = st.multiselect("Selecione os passageiros:", options=lista_p)

    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "motorista"]
    cols_outros = ["passageiro", "trajeto", "semana", "data", "horário", "motorista"]

    # --- 📄 GERADOR DO BOTÃO DE SALVAR PDF/HTML (RETORNADO) ---
    html_relatorio = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
            h2 {{ text-align: center; color: #002D5E; border-bottom: 2px solid #FF7F50; padding-bottom: 5px; }}
            h3 {{ background-color: #002D5E; color: white; padding: 8px; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 12px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; text-transform: uppercase; }}
            .obs-box {{ margin-bottom: 8px; padding: 5px; border-left: 3px solid #FF7F50; }}
        </style>
    </head>
    <body>
        <h2>AURA APOENA LOGISTICS - AGENDA CORPORATIVA</h2>
        <p>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        <h3>OBSERVAÇÕES DA SEMANA</h3>
    """
    for _, r_obs in df_o.iterrows():
        texto_obs = str(r_obs.get('observacao', '')).strip()
        if texto_obs and texto_obs != "nan":
            html_relatorio += f"<div class='obs-box'><b>{r_obs.get('dia', '')} ({r_obs.get('data', '')}):</b><br>{texto_obs.replace('\n', '<br>')}</div>"
            
    def criar_tabela_html(titulo, df_origem, colunas, condicao):
        html = f"<h3>{titulo}</h3>"
        if df_origem.empty:
            return html + "<p>Nenhuma viagem programada.</p>"
        df_seguro = verificar_colunas_html(df_origem, colunas)
        html += "<table><tr>" + "".join(f"<th>{c}</th>" for c in colunas) + "</tr>"
        for _, row in df_seguro.iterrows():
            html += "<tr>" + "".join(f"<td>{str(row[c]) if pd.notna(row[c]) else ''}</td>" for c in colunas) + "</tr>"
        return html + "</table>"

    def verificar_colunas_html(df_alvo, colunas):
        df_c = df_alvo.copy()
        for c in colunas:
            if c not in df_c.columns: df_c[c] = ""
        return df_c[colunas]

    html_relatorio += criar_tabela_html("PONTES E LACERDA X CUIABÁ", df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"], cols_pl, "pl")
    html_relatorio += criar_tabela_html("CUIABÁ X PONTES E LACERDA", df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"], cols_cp, "cp")
    html_relatorio += criar_tabela_html("OUTROS TRAJETOS E CIDADES", df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])], cols_outros, "outros")
    html_relatorio += "</body></html>"

    st.download_button(
        label="📄 Baixar Relatório Unificado da Agenda (PDF/HTML)",
        data=html_relatorio,
        file_name=f"agenda_aura_{datetime.now().strftime('%d_%m_%Y')}.html",
        mime="text/html",
        use_container_width=True
    )
    # ---------------------------------------------------------

    st.markdown("---")

    # Tabelas de Exibição na Tela
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"]
    st.dataframe(corrigir_colunas_faltantes(df_pl, cols_pl), use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"]
    st.dataframe(corrigir_colunas_faltantes(df_cp, cols_cp), use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho
