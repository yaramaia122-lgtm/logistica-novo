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

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    novas_obs = []
    for idx, row in df_o.iterrows():
        c1, c2, c3 = st.columns([1.5, 1, 6.5])
        c1.markdown(f"<p style='padding-top:15px; font-weight:bold;'>{row.get('dia', row.get('Dia', ''))}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='padding-top:15px; color:#555555;'>{row.get('data', row.get('Data', ''))}</p>", unsafe_allow_html=True)
        novas_obs.append(c3.text_area(label=f"O_{idx}", value=str(row.get('observacao', row.get('Observacao', ''))), key=f"obs_{idx}", label_visibility="collapsed"))

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Obs", df_o.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Salvo!"); st.rerun()

    st.markdown("---")
    
    # Encontra a coluna de trajeto e passageiro indepedente de maiúscula/minúscula
    col_t = next((c for c in df_v.columns if str(c).strip().lower() == "trajeto"), "trajeto")
    col_p = next((c for c in df_v.columns if str(c).strip().lower() == "passageiro"), "passageiro")

    p_sel = st.multiselect("Filtrar por Passageiro:", options=sorted(list(df_v[col_p].dropna().unique())))
    df_f = df_v[df_v[col_p].isin(p_sel)] if p_sel else df_v

    # Filtros baseados puramente no texto da planilha
    df_pl = df_f[df_f[col_t].astype(str).str.strip().str.lower() == "pontes e lacerda x cuiabá"]
    df_cp = df_f[df_f[col_t].astype(str).str.strip().str.lower() == "cuiabá x pontes e lacerda"]
    df_out = df_f[~df_f[col_t].astype(str).str.strip().str.lower().isin(["pontes e lacerda x cuiabá", "cuiabá x pontes e lacerda"])]

    st.markdown('<div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_pl.dropna(how='all', axis=1), width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_cp.dropna(how='all', axis=1), width='stretch', hide_index=True)

    st.markdown('<div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_out.dropna(how='all', axis=1), width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
