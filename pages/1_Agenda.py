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
    
    file_log = rp.get_contents("dados_logistica.csv")
    df_v = pd.read_csv(io.StringIO(file_log.decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(rp.get_contents("observacoes.csv").decoded_content.decode()))

    df_o.columns = df_o.columns.str.strip().str.lower()
    df_o = df_o.loc[:, ~df_o.columns.duplicated()]
    for c in ["dia", "data", "observacao"]: 
        if c in df_o.columns: df_o[c] = df_o[c].fillna("").astype(str).str.strip()

    # 🕒 Controle da Semana com base na escolha do usuário
    fuso = zoneinfo.ZoneInfo("America/Cuiaba")
    hoje_fuso = datetime.now(fuso).date()
    
    st.write("### 📅 Período da Agenda")
    data_selecionada = st.date_input("Visualizar agenda a partir do dia:", value=hoje_fuso)
    
    segunda = data_selecionada - timedelta(days=data_selecionada.weekday())
    dias_s = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    datas_s = [(segunda + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]

    dados_obs = []
    obs_dict = dict(zip(df_o["dia"].str.strip().str.lower(), df_o["observacao"].fillna("")))
    for i, dia in enumerate(dias_s):
        dados_obs.append({"dia": dia, "data": datas_s[i], "observacao": obs_dict.get(dia.lower(), "")})
    df_o_atualizado = pd.DataFrame(dados_obs)

    st.markdown('<div class="agenda-header">Observações Semanais</div>', unsafe_allow_html=True)
    df_o_edit = st.data_editor(df_o_atualizado, column_config={"dia": st.column_config.TextColumn("Dia da Semana", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "observacao": st.column_config.TextColumn("Observação", width="large")}, hide_index=True, width='stretch', row_height=100, key="ed_obs_v26")

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        rp.update_file("observacoes.csv", "Update", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Observações salvas!"); st.rerun()

    st.markdown("---")
    
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    if "status" not in df_v.columns: df_v["status"] = "Confirmado"
    df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
    df_v = df_v.fillna("").astype(str)

    st.write("### ⚙️ Gerenciar Status de Viagens (Cancelamentos / Ocultar)")
    lista_geral = [f"{i} - {row['passageiro']} ({row['data']} | {row['trajeto']}) [{row['status']}]" for i, row in df_v.iterrows() if row['passageiro'] != ""]
    col_sel, col_status = st.columns([2, 1])
    viagem_selecionada = col_sel.selectbox("Selecione a viagem para alterar:", options=[""] + lista_geral)
    novo_status = col_status.selectbox("Mudar status para:", ["Confirmado", "Cancelado", "Ocultado"])
    
    if st.button("⚠️ Atualizar Status da Viagem Selecionada", width='stretch'):
        if viagem_selecionada:
            idx = int(viagem_selecionada.split(" - ")[0])
            df_v.at[idx, "status"] = novo_status
            rp.update_file("dados_logistica.csv", "Status updated", df_v.to_csv(index=False), file_log.sha)
            st.success("Status atualizado!"); st.rerun()

    st.markdown("---")

    # Filtros e exibição das viagens baseadas nas datas da semana selecionada
    df_f_visivel = df_v[df_v["status"] == "Confirmado"]
    df_f_semana = df_f_visivel
