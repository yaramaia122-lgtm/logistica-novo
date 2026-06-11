import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

# Estilo original compactado para evitar bloqueio de sincronização
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .trecho-header { background-color: #002D5E !important; color: white !important; padding: 8px 12px; font-weight: bold; border-radius: 4px; margin-top: 15px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

def limpar_e_garantir(df_alvo, colunas_alvo):
    df_temp = pd.DataFrame()
    for col in colunas_alvo:
        # Busca a coluna ignorando maiúsculas/minúsculas
        match_col = next((c for c in df_alvo.columns if str(c).strip().lower() == col.lower()), None)
        if match_col:
            df_temp[col] = df_alvo[match_col].fillna("").astype(str).str.strip()
        else:
            df_temp[col] = ""
    return df_temp[colunas_alvo]

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
        c1.markdown(f"<p style='padding-top:15px; font-weight:bold;'>{row.get('dia', '')}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='padding-top:15px; color:#555555;'>{row.get('data', '')}</p>", unsafe_allow_html=True)
        novas_obs.append(c3.text_area(label=f"O_{idx}", value=str(row.get('observacao', '')), key=f"obs_{idx}", label_visibility="collapsed"))

    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Obs", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    lista_p = sorted([p for p in df_v["passageiro"].unique() if str(p).strip() != ""]) if "passageiro" in df_v.columns else []
    p_sel = st.multiselect("Filtrar por Passageiro:", options=lista_p)
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v
    df_f["trajeto"] = df_f["trajeto"].fillna("").astype(str).str.strip().str.lower() if "trajeto" in df_f.columns else ""

    # Relatório em HTML
    html_res = f"<html><body><h2>AURA LOGISTICS</h2>{df_f.to_html(index=False, border=1)}</body></html>"
    st.download_button(label="📄 Baixar Relatório da Agenda (HTML)", data=html_res, file_name="agenda.html", mime="text/html", use_container_width=True)

    # Definindo as colunas fiéis à sua planilha original do Excel para cada caso
    cols_pl = ["passageiro", "semana", "data", "horário", "saída", "cia/nº voo", "horário do voo", "data do voo", "hotel em cuiabá", "motorista"]
    cols_cp = ["passageiro", "semana", "data", "horário", "cia/nº voo", "hotel cuiabá", "semana", "data", "horário", "motorista", "hospedagem . lacerda"]
    cols_out = ["passageiro", "trajeto", "semana", "data", "horário", "cia/nº voo", "horário do voo", "motorista"]

    # Renderização das tabelas com os títulos nas cores originais da Aura
    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_f[df_f['trajeto'] == "pontes e lacerda x cuiabá"]
    st.dataframe(limpar_e_garantir(df_pl, cols_pl), use_container_width=True, hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_f[df_f['trajeto'] == "cuiabá x pontes e lacerda"]
    st.dataframe(limpar_e_garantir(df_cp, cols_cp), use_container_width=True, hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_out = df_f[~df_f['trajeto'].isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])]
    st.dataframe(limpar_e_garantir(df_out, cols_out), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
