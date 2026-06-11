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

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 0px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    div[data-testid="stTextArea"] textarea { background-color: #FFFFFF !important; color: #000000 !important; font-family: sans-serif !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

def corrigir_colunas_faltantes(df_alvo, colunas_requisitadas):
    df_temp = df_alvo.copy()
    for col in colunas_requisitadas:
        if col not in df_temp.columns: 
            df_temp[col] = ""
    return df_temp[colunas_requisitadas]

def gerar_tabela_html(titulo, df_sub, colunas):
    txt = "<h3>" + str(titulo) + "</h3>"
    if df_sub.empty:
        return txt + "<p style='font-size:12px; color:#666;'>Nenhuma viagem programada.</p>"
    df_seguro = df_sub.copy()
    for c in colunas:
        if c not in df_seguro.columns: 
            df_seguro[c] = ""
    txt += "<table><tr>"
    for c in colunas:
        txt += "<th>" + str(c) + "</th>"
    txt += "</tr>"
    for _, row in df_seguro[colunas].iterrows():
        txt += "<tr>"
        for c in colunas:
            val = row[c]
            txt += "<td>" + (str(val) if pd.notna(val) else "") + "</td>"
        txt += "</tr>"
    txt += "</table>"
    return txt

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo_nome = st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo_nome)

    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_v.columns = df_v.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    df_v["passageiro"] = df_v["passageiro"].fillna("").astype(str).str.strip() if "passageiro" in df_v.columns else ""
    df_v["trajeto"] = df_v["trajeto"].fillna("").astype(str).str.strip().str.lower() if "trajeto" in df_v.columns else ""

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        c_dia.markdown("<p style='padding-top:15px; font-weight:bold; color:#333333;'>" + str(row.get('dia', '')) + "</p>", unsafe_allow_html=True)
        c_data.markdown("<p style='padding-top:15px; color:#555555;'>" + str(row.get('data', '')) + "</p>", unsafe_allow_html=True)
        t_val = row.get('observacao', '')
        t = c_texto.text_area(label="Obs_" + str(index), value=t_val if pd.notna(t_val) else "", key="obs_" + str(index), label_visibility="collapsed")
        novas_obs.append(t)

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Obs", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Observações salvas!")
        st.rerun()

    st.markdown("---")
    st.write("### 🔍 Filtrar Programação por Passageiros")
    lista_p = sorted([p for p in df_v["passageiro"].unique() if p != ""])
    p_sel = st.multiselect("Selecione os passageiros:", options=lista_p)

    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # 🛡️ EXPANSÃO TÉCNICA DAS COLUNAS (Inclusão de voo e horário do voo)
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]
    cols_outros = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    # Montagem do Relatório Elaborado
    data_hoje = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    html_relatorio = "<html><head><meta charset='utf-8'><style>"
    html_relatorio += "body { font-family: Arial, sans-serif; margin: 20px; color: #333; }"
    html_relatorio += "h2 { text-align: center; color: #002D5E; border-bottom: 2px solid #FF7F50; padding-bottom: 5px; }"
    html_relatorio += "h3 { background-color: #002D5E; color: white; padding: 8px; margin-top: 20px; text-transform: uppercase; font-size: 14px; }"
    html_relatorio += "table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 12px; }"
    html_relatorio += "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }"
    html_relatorio += "th { background-color: #f2f2f2; font-weight: bold; text-transform: uppercase; }"
    html_relatorio += ".obs-box { margin-bottom: 8px; padding: 8px; border-left: 4px solid #FF7F50; background-color: #f9f9f9; }"
    html_relatorio += "</style></head><body>"
    html_relatorio += "<h2>AURA APOENA LOGISTICS - AGENDA CORPORATIVA</h2><p>Relatório gerado em: " + str(data_hoje) + "</p><h3>OBSERVAÇÕES DA SEMANA</h3>"

    for _, r_obs in df_o.iterrows():
        t_obs = str(r_obs.get('observacao', '')).strip()
        if t_obs and t_obs != "nan" and t_obs != "":
            html_relatorio += "<div class='obs-box'><b>" + str(r_obs.get('dia', '')) + " (" + str(r_obs.get('data', '')) + "):</b><br>" + t_obs.replace('\n', '<br>') + "</div>"

    html_relatorio += gerar_tabela_html("PONTES E LACERDA X CUIABÁ", df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"], cols_pl)
    html_relatorio += gerar_tabela_html("CUIABÁ X PONTES E LACERDA", df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"], cols_cp)
    html_relatorio += gerar_tabela_html("OUTROS TRAJETOS E CIDADES", df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])], cols_outros)
    html_relatorio += "</body></html>"

    st.download_button(
        label="📄 Baixar Relatório Unificado da Agenda (PDF/HTML)",
        data=html_relatorio,
        file_name="agenda_aura_" + datetime.now().strftime('%d_%m_%Y') + ".html",
        mime="text/html",
        use_container_width=True
    )

    st.markdown("---")

    # Exibição segura das tabelas na tela contendo as colunas de voo
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl_screen = df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"]
    st.dataframe(corrigir_colunas_faltantes(df_pl_screen, cols_pl), use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp_screen = df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"]
    st.dataframe(corrigir_colunas_faltantes(df_cp_screen, cols_cp), use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros_screen = df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])]
    st.dataframe(corrigir_colunas_faltantes(df_outros_screen, cols_outros), use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Erro na conexão com o banco de dados: " + str(e))
