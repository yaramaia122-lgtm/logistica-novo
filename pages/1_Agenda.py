import streamlit as st
import pandas as pd
from github import Github, Auth
import io
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

# Estilização CSS Corporativa e Ocultação Absoluta para Geração de PDF limpo
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
    
    /* Remove as bordas feias e caixas cinzas das áreas de texto na hora de exibir e imprimir */
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: sans-serif !important;
        font-size: 14px !important;
    }
    
    /* Regras de Impressão de Alta Precisão (Sume com botões e menus no PDF) */
    @media print {
        section[data-testid="stSidebar"], 
        button[data-testid="sidebar-toggle"],
        header, 
        footer,
        div.stButton,
        .no-print { 
            display: none !important; 
        }
        .stApp { background-color: white !important; }
        div[data-testid="stTextArea"] textarea {
            border: none !important;
            box-shadow: none !important;
            padding: 0px !important;
        }
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

    # Estruturação rígida e limpa de dias caso o arquivo esteja vazio
    dias_semana_nome = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    if df_o.empty or len(df_o) < 7:
        dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        df_o = pd.DataFrame({"Dia": dias_semana_nome, "Data": dias_v, "Observacao": [""]*7})
    
    df_o["Observacao"] = df_o["Observacao"].astype(str).replace("nan", "")

    # Painel Superior de Título das Observações
    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    
    # Construção das linhas expandidas dinamicamente baseada na imagem de referência
    novas_obs = []
    for index, row in df_o.iterrows():
        c_dia, c_data, c_texto = st.columns([1.5, 1, 6.5])
        with c_dia:
            st.markdown(f"<p style='padding-top:15px; font-weight:bold; color:#333333;'>{row['Dia']}</p>", unsafe_allow_html=True)
        with c_data:
            st.markdown(f"<p style='padding-top:15px; color:#555555;'>{row['Data']}</p>", unsafe_allow_html=True)
        with c_texto:
            # st.text_area expande verticalmente aceitando múltiplos Enters/Alt+Enters
            texto_inserido = st.text_area(
                label=f"Obs {row['Dia']}", 
                value=row['Observacao'], 
                key=f"obs_{index}", 
                label_visibility="collapsed"
            )
            novas_obs.append(texto_inserido)
        st.markdown("<hr style='margin: 0px 0px 5px 0px; border-color:#E0E0E0;'>", unsafe_allow_html=True)

    # Botão de Salvamento - Enquadrado na classe CSS para não sair na impressão
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    if st.button("💾 Salvar Alterações das Observações", use_container_width=True):
        df_o["Observacao"] = novas_obs
        rp.update_file("observacoes.csv", "Update Observacoes", df_o.to_csv(index=False), f_o.sha)
        st.success("Observações sincronizadas com o banco de dados."); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Seção de Filtros (Ocultada por padrão no PDF final)
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    st.write("### Filtrar e Exportar")
    passageiro_filtro = st.text_input("Digite o nome do passageiro para filtrar (Deixe em branco para ver todos):").strip().upper()
    
    # Disparador nativo estável de impressão (Abre o salvar como PDF do sistema operacional)
    if st.button("🖨️ Emitir Documento Oficial da Agenda (Salvar como PDF)", use_container_width=True):
        st.components.v1.html("<script>window.print();</script>", height=0, width=0)
    st.markdown('</div>', unsafe_allow_html=True)

    # Filtragem inteligente dos trechos
    if passageiro_filtro:
        df_filtrado = df_v[df_v['Passageiro'].astype(str).str.contains(passageiro_filtro, na=False)]
    else:
        df_filtrado = df_v

    # Exibição de Tabelas Operacionais
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_filtrado[df_filtrado['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
    cols_pl = ["Passageiro", "semana", "data", "horário", "saída", "Cia/nº voo", "Horário do Voo", "Data do Voo", "Hotel em Cuiabá", "Motorista"]
    for c in cols_pl:
        if c not in df_pl.columns: df_pl[c] = ""
    st.dataframe(df_pl[cols_pl], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_filtrado[df_filtrado['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
    cols_cp = ["Passageiro", "semana", "data", "horário", "Cia/nº voo", "Hotel Cuiabá", "semana_ret", "data_ret", "horário_ret", "Motorista", "Hospedagem . Lacerda"]
    for c in cols_cp:
        if c not in df_cp.columns: df_cp[c] = ""
    st.dataframe(df_cp[cols_cp], use_container_width=True, hide_index=True)

    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros = df_filtrado[~df_filtrado['Trajeto'].isin(["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda"])]
    cols_outros = ["Passageiro", "Trajeto", "semana", "data", "horário", "saída", "Motorista", "Hotel em Cuiabá"]
    for c in cols_outros:
        if c not in df_outros.columns: df_outros[c] = ""
    st.dataframe(df_outros[cols_outros], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro na conexão com o banco de dados: {e}")
