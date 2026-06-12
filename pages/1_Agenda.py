import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 8px 12px; font-weight: bold; border-radius: 4px; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    st.markdown('<div class="agenda-header">Observações</div>', unsafe_allow_html=True)
    
    # Exibe as observações exatamente como no modelo de planilha image_b2ba1b.png
    df_o_edit = st.data_editor(
        df_o[["dia", "data", "observacao"]],
        column_config={
            "dia": st.column_config.TextColumn("Dia da Semana", disabled=True),
            "data": st.column_config.TextColumn("Data", disabled=True),
            "observacao": st.column_config.TextColumn("Observação", width="large")
        },
        hide_index=True, use_container_width=True, key="ed_obs"
    )

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["observacao"] = df_o_edit["observacao"]
        rp.update_file("observacoes.csv", "Update", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    
    p_sel = st.multiselect("Filtrar por Passageiro:", options=sorted(list(df_v["passageiro"].dropna().unique())))
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # Suas colunas de controle por trecho de volta
    c_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "motorista"]
    c_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "horário do voo", "hotel cuiabá", "semana.1", "data.1", "horário.1", "motorista", "hospedagem . lacerda"]
    c_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    for c in list(set(c_pl + c_cp + c_out)):
        if c not in df_f.columns: df_f[c] = ""
        else: df_f[c] = df_f[c].fillna("").astype(str).str.strip()

    df_pl_r = df_f[df_f['trajeto'].str.lower() == "pontes e lacerda x cuiabá"][c_pl]
    df_cp_r = df_f[df_f['trajeto'].str.lower() == "cuiabá x pontes e lacerda"][c_cp]
    df_out_r = df_f[~df_f['trajeto'].str.lower().isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])][c_out]

    # Botão de Relatório HTML simples e leve para não estourar a sincronização
    html_data = "<h2>AURA LOGISTICS</h2>" + df_pl_r.to_html(index=False) + df_cp_r.to_html(index=False)
    st.download_button(label="📄 Baixar Relatório da Agenda (HTML)", data=html_data, file_name="agenda.html", mime="text/html", use_container_width=True)

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_pl_r, use_container_width=True, hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_cp_r, use_container_width=True, hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_out_r, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro: {e}")
