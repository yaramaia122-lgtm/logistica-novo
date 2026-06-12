import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Agenda - AURA", layout="wide")

# Estilos CSS em blocos pequenos
st.markdown("<style>.stApp { background-color: #F0F8FF !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.agenda-header { background-color: #FF7F50 !important; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.treche-header { background-color: #002D5E !important; color: white !important; padding: 6px 12px; font-weight: bold; border-radius: 4px; margin-top: 12px; }</style>", unsafe_allow_html=True)

try:
    tk = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    g = Github(auth=Auth.Token(tk))
    rp = g.get_repo(repo)
    
    # Carrega arquivos
    f_v = rp.get_contents("dados_logistica.csv")
    f_o = rp.get_contents("observacoes.csv")
    df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))
    df_o = pd.read_csv(io.StringIO(f_o.decoded_content.decode()))

    # Ajusta as observacoes
    df_o.columns = df_o.columns.str.strip().str.lower()
    df_o = df_o.loc[:, ~df_o.columns.duplicated()]
    for c in ["dia", "data", "observacao"]:
        if c in df_o.columns:
            df_o[c] = df_o[c].fillna("").astype(str).str.strip()

    st.markdown('<div class="agenda-header">Observações</div>', unsafe_allow_html=True)
    
    df_o_edit = st.data_editor(
        df_o[["dia", "data", "observacao"]],
        hide_index=True,
        width='stretch',
        row_height=100,
        key="ed_obs_v21"
    )

    if st.button("💾 Salvar Alterações das Observações", width='stretch'):
        df_o["observacao"] = df_o_edit["observacao"]
        rp.update_file("observacoes.csv", "Update", df_o.to_csv(index=False), f_o.sha)
        st.success("Salvo!")
        st.rerun()

    st.markdown("---")
    
    # Ajusta o arquivo principal de viagens
    df_v.columns = df_v.columns.str.strip().str.lower()
    df_v = df_v.loc[:, ~df_v.columns.duplicated()]
    df_v = df_v.fillna("").astype(str)

    p_list = sorted(list(df_v["passageiro"].unique()))
    p_sel = st.multiselect("Filtrar por Passageiro:", options=p_list)
    
    df_f = df_v[df_v['passageiro'].isin(p_sel)] if p_sel else df_v

    # Esconde colunas financeiras de forma automática e direta
    cols_ok = [c for c in df_f.columns if "r$" not in c and "custo" not in c]
    df_disp = df_f[cols_ok]

    t_str = df_disp['trajeto'].str.strip().str.lower().str.replace("á", "a")

    # Dicionario de nomes limpos para exibição nas tabelas
    n_col = {
        "horario": "Horário",
        "saida": "Saída",
        "cia/n vuo": "Cia/Nº Voo",
        "horario do vuo": "Horário do Voo",
        "data do vuo": "Data do Voo",
        "hotel em cuiaba": "Hotel em Cuiabá",
        "hotel cuiaba": "Hotel Cuiabá",
        "hospedagem . lacerda": "Hospedagem P. Lacerda",
        "semana.1": "Semana Retorno",
        "data.1": "Data Retorno",
        "horario.1": "Horário Retorno"
    }

    # Renderiza os blocos na tela de forma isolada e segura
    st.markdown('<div class="treche-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_disp[t_str == "pontes e lacerda x cuiaba"]
    st.dataframe(df_pl.rename(columns=n_col), width='stretch', hide_index=True)

    st.markdown('<div class="treche-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_disp[t_str == "cuiaba x pontes e lacerda"]
    st.dataframe(df_cp.rename(columns=n_col), width='stretch', hide_index=True)

    st.markdown('<div class="treche-header">OUTROS TRAJETOS E CIDADES</div>', unsafe_allow_html=True)
    df_out = df_disp[(t_str != "pontes e lacerda x cuiaba") & (t_str != "cuiaba x pontes e lacerda")]
    st.dataframe(df_out.rename(columns=n_col), width='stretch', hide_index=True)

except Exception as e:
    st.error(f"Erro no banco de dados: {e}")
