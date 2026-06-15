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

    # Ajuste das observações
    df_o.columns = df_o.columns.str.strip().str.lower()
    df_o = df_o.loc[:, ~df_o.columns.duplicated()]
    for c in ["dia", "data", "observacao"]: 
        if c in df_o.columns: df_o[c] = df_o[c].fillna("").astype(str).str.strip()

    st.markdown('<div class="agenda-header">Observações Semanais</div>', unsafe_allow_html=True)
    df_o_edit = st.data_editor(df_o[["dia", "data", "observacao"]], hide_index=True, width='stretch', row_height=100, key="ed_obs_v24")

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        rp.update_file("observacoes.csv", "Update", df_o_edit.to_csv(index=False), rp.get_contents("observacoes.csv").sha)
        st.success("Observações salvas!"); st.rerun()

    st.markdown("---")
    
    # Processamento e padronização das viagens
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    
    # Garante que a coluna status exista
    if "status" not in df_v.columns: df_v["status"] = "Confirmado"
    df_v["status"] = df_v["status"].fillna("Confirmado").astype(str).str.strip()
    df_v = df_v.fillna("").astype(str)

    # 🔄 PAINEL EXCLUSIVO PARA GERENCIAR CANCELAMENTOS
    st.write("### ⚙️ Gerenciar Status de Viagens (Cancelamentos / Ocultar)")
    lista_geral = [f"{i} - {row['passageiro']} ({row['data']} | {row['trajeto']}) [{row['status']}]" for i, row in df_v.iterrows() if row['passageiro'] != ""]
    
    col_sel, col_status = st.columns([2, 1])
    viagem_selecionada = col_sel.selectbox("Selecione a viagem para alterar:", options=[""] + lista_geral)
    novo_status = col_status.selectbox("Mudar status para:", ["Confirmado", "Cancelado", "Ocultado"])
    
    if st.button("⚠️ Atualizar Status da Viagem Selecionada", width='stretch'):
        if viagem_selecionada:
            idx = int(viagem_selecionada.split(" - ")[0])
            df_v.at[idx, "status"] = novo_status
            rp.update_file("dados_logistica.csv", "Status atualizado", df_v.to_csv(index=False), file_log.sha)
            st.success(f"Status atualizado para {novo_status} com sucesso!"); st.rerun()
        else:
            st.error("Selecione uma viagem primeiro.")

    st.markdown("---")

    # Filtro por passageiro normal
    p_sel = st.multiselect("Filtrar Visualização por Passageiro:", options=sorted(list(df_v["passageiro"].unique())))
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # 🛡️ FILTRO CRÍTICO: Esconde da agenda qualquer viagem cancelada ou ocultada
    df_f_visivel = df_f[df_f["status"] == "Confirmado"]

    cols_exibir = [c for c in df_f_visivel.columns if "r$" not in c and "custo" not in c and "valor" not in c and "status" not in c]
    df_limpo = df_f_visivel[cols_exibir]

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
