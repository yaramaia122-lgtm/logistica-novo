import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# Proteção de acesso direto via URL
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.set_page_config(page_title="Acesso Negado", layout="wide")
    st.warning("Por favor, realize o login para acessar esta página.")
    st.stop()

st.set_page_config(page_title="Agenda - AURA", layout="wide", initial_sidebar_state="expanded")

# Menu Lateral Corporativo com Botão de Sair Formalizado
with st.sidebar:
    st.write(f"Usuário ativo: **{st.session_state.get('user', 'Funcionário')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['user'] = None
        st.switch_page("main.py")

# Estilização CSS Corporativa
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header {
        background-color: #FF7F50 !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
        margin-bottom: 0px;
    }
    .trecho-header {
        background-color: #002D5E !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: sans-serif !important;
        font-size: 14px !important;
    }
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

    # Tratamento de valores nulos e strings para evitar quebras
    df_v["Passageiro"] = df_v["Passageiro"].fillna("").astype(str)
    
    dias_semana_nome = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    
    if "Dia" not in df_o.columns or df_o.empty or len(df_o) < 7:
        dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        textos_antigos = df_o["Observacao"].tolist() if "Observacao" in df_o.columns else [""]*7
        if len(textos_antigos) < 7: textos_antigos += [""] * (7 - len(textos_antigos))
        df_o = pd.DataFrame({"Dia": dias_semana_nome, "Data": dias_v, "Observacao": textos_antigos[:7]})
    
    df_o["Observacao"] = df_o["Observacao"].fillna("").astype(str)

    # Painel de Observações da Semana
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        with c_dia:
            st.markdown(f"<p style='padding-top:15px; font-weight:bold; color:#333333;'>{row['Dia']}</p>", unsafe_allow_html=True)
        with c_data:
            st.markdown(f"<p style='padding-top:15px; color:#555555;'>{row['Data']}</p>", unsafe_allow_html=True)
        with c_texto:
            texto_inserido = st.text_area(label=f"Obs {row['Dia']}", value=row['Observacao'], key=f"obs_{index}", label_visibility="collapsed")
            novas_obs.append(texto_inserido)
        st.markdown("<hr style='margin: 0px 0px 5px 0px; border-color:#E0E0E0;'>", unsafe_allow_html=True)

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["Observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Observacoes", df_o.to_csv(index=False), f_o.sha)
        st.success("Observações sincronizadas com sucesso."); st.rerun()

    st.markdown("---")
    
    # --- FILTRO MULTI-SELEÇÃO ESTILO EXCEL ---
    st.write("### 🔍 Filtrar Programação por Passageiros")
    
    lista_passageiros = sorted([p for p in df_v["Passageiro"].unique() if p.strip() != ""])
    
    passageiros_selecionados = st.multiselect(
        "Selecione um ou mais passageiros (Deixe vazio para mostrar todos):",
        options=lista_passageiros
    )

    if passageiros_selecionados:
        df_filtrado = df_v[df_v['Passageiro'].isin(passageiros_selecionados)]
    else:
        df_filtrado = df_v

    # --- 📄 GERADOR DO ARQUIVO UNIFICADO (HTML/PDF) ---
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
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .obs-box {{ margin-bottom: 8px; padding: 5px; border-left: 3px solid #FF7F50; }}
        </style>
    </head>
    <body>
        <h2>AURA APOENA LOGISTICS - AGENDA CORPORATIVA</h2>
        <p>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        
        <h3>OBSERVAÇÕES DA SEMANA</h3>
    """
    for _, r_obs in df_o.iterrows():
        texto_obs = str(r_obs['Observacao']).strip()
        if texto_obs:
            obs_formatada = texto_obs.replace('\n', '<br>')
            html_relatorio += f"<div class='obs-box'><b>{r_obs['Dia']} ({r_obs['Data']}):</b><br>{obs_formatada}</div>"
            
    def adicionar_tabela_html(titulo, dataframe, colunas):
        global html_relatorio
        html_relatorio += f"<h3>{titulo}</h3>"
        if dataframe.empty:
            html_relatorio += "<p>Nenhuma viagem programada para este trecho.</p>"
            return
        df_html = dataframe[colunas].copy()
        for c in colunas:
            if c not in df_html.columns: df_html[c] = ""
        html_relatorio += "<table><tr>" + "".join(f"<th>{c}</th>" for c in colunas) + "</tr>"
        for _, row in df_html.iterrows():
            html_relatorio += "<tr>" + "".join(f"<td>{str(row[c]) if pd.notna(row[c]) else ''}</td>" for c in colunas) + "</tr>"
        html_relatorio += "</table>"

    cols_pl = ["Passageiro", "semana", "data", "horário", "saída", "Motorista"]
    cols_cp = ["Passageiro", "semana", "data", "horário", "Motorista"]
    cols_outros = ["Passageiro", "Trajeto", "semana", "data", "horário", "Motorista"]

    adicionar_tabela_html("PONTES E LACERDA X CUIABÁ", df_filtrado[df_filtrado['Trajeto'] == "Pontes e Lacerda x Cuiabá"], cols_pl)
    adicionar_tabela_html("CUIABÁ X PONTES E LACERDA", df_filtrado[df_filtrado['Trajeto'] == "Cuiabá x Pontes e Lacerda"], cols_cp)
    adicionar_tabela_html("OUTROS TRAJETOS E CIDADES", df_filtrado[~df_filtrado['Trajeto'].isin(["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda"])], cols_outros)

    html_relatorio += "</body></html>"

    # Botão de download direto do arquivo de Agenda Consolidadado
    st.download_button(
        label="📄 Baixar Relatório Unificado da Agenda (HTML/PDF)",
        data=html_relatorio,
        file_name=f"agenda_aura_{datetime.now().strftime('%d_%m_%Y')}.html",
        mime="text/html",
        use_container_width=True
    )

    st.markdown("---")

    # Exibição das Tabelas na Tela
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl_screen = df_filtrado[df_filtrado['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
    for c in cols_pl:
        if c not in df_pl_screen.columns: df_pl_screen[c] = ""
    st.dataframe(df_pl_screen[cols_pl], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp_screen = df_filtrado[df_filtrado['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
    for c in cols_cp:
        if c not in df_cp_screen.columns: df_cp_screen[c] = ""
    st.dataframe(df_cp_screen[cols_cp], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros_screen = df_filtrado[~df_filtrado['Trajeto'].isin(["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda"])]
    for c in cols_outros:
        if c not in df_outros_screen.columns: df_outros_screen[c] = ""
    st.dataframe(df_outros_screen[cols_outros], use_container_width=True, hide_index=True)

except Exception as e:
    st
