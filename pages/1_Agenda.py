import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta
import zoneinfo

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False; st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
    .treche-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; border-radius: 4px; margin-top: 12px; }
</style>""", unsafe_allow_html=True)

try:
    tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
    
    df_v = pd.read_csv(io.StringIO(rp.get_contents("dados_logistica.csv").decoded_content.decode()))
    
    # 🕒 CALCULA A SEMANA ATUAL DE CUIABÁ AUTOMATICAMENTE
    fuso = zoneinfo.ZoneInfo("America/Cuiaba")
    hoje = datetime.now(fuso).date()
    segunda = hoje - timedelta(days=hoje.weekday())
    
    dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    datas_semana = [(segunda + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
    
    # Tenta ler o arquivo de observações existente
    try:
        df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))
        df_o.columns = df_o.columns.str.strip().str.lower()
        obs_dict = dict(zip(df_o["dia"].str.strip().str.lower(), df_o["observacao"].fillna("")))
    except:
        obs_dict = {}

    # Monta a estrutura da planilha com as datas corrigidas e automáticas de hoje
    dados_obs = []
    for i, dia in enumerate(dias_semana):
        texto_obs = obs_dict.get(dia.lower(), "")
        dados_obs.append({"dia": dia, "data": datas_semana[i], "observacao": texto_obs})
    df_o_atualizado = pd.DataFrame(dados_obs)

    st.markdown('<div class="agenda-header">Observações Semanais</div>', unsafe_allow_html=True)
    df_o_edit = st.data_editor(df_o_atualizado, column_config={"dia": st.column_config.TextColumn("Dia da Semana", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "observacao": st.column_config.TextColumn("Observação", width="large")}, hide_index=True, width='stretch', row_height=100, key="ed_obs_v23")

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        rp.update_file("observacoes.csv", "Update", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Observações salvas!"); st.rerun()

    st.markdown("---")
    
    # Processamento padrão das viagens por trecho
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()].fillna("").astype(str)

    p_sel = st.multiselect("Filtrar por Passageiro:", options=sorted(list(df_v["passageiro"].unique())))
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    cols_exibir = [c for c in df_f.columns if "r$" not in c and "custo" not in c and "valor" not in c]
    df_limpo = df_f[cols_exibir]

    n_col = {"passageiro": "Passageiro", "trajeto": "Trajeto", "semana": "Semana", "data": "Data", "horario": "Horário", "saida": "Saída", "cia/nº voo": "Cia/Nº Voo", "horario do vuo": "Horário do Voo", "data do vuo": "Data do Voo", "hotel em cuiaba": "Hotel em Cuiabá", "hotel cuiaba": "Hotel Cuiabá", "motorista": "Motorista"}
    t_str = df_limpo['trajeto'].str.strip().str.lower().str.replace("á", "a")

    st.markdown('<div class="treche-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    st.dataframe(df_limpo[t_str == "pontes e lacerda x cuiaba"].rename(columns=n_col), width='stretch', hide_index=True)

    st.markdown('<div class="treche-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    st.dataframe(df_limpo[t_str == "cuiaba x pontes e lacerda"].rename(columns=n_col), width='stretch', hide_index=True)

    st.markdown('<div class="treche-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    st.dataframe(df_limpo[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")].rename(columns=n_col), width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
