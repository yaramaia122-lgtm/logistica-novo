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

# Estilização CSS com regras de impressão (PDF) inclusas
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF !important; }
    .agenda-header {
        background-color: #FF7F50 !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .trecho-header {
        background-color: #002D5E !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    
    /* Regras especiais para quando for salvar em PDF / Imprimir */
    @media print {
        section[data-testid="stSidebar"] { display: none !important; }
        button[data-testid="sidebar-toggle"] { display: none !important; }
        .stButton { display: none !important; }
        div[data-testid="stToolbar"] { display: none !important; }
        header { display: none !important; }
        .stApp { background-color: white !important; }
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

    # --- CORREÇÃO DAS OBSERVAÇÕES ---
    # Garante que a tabela de observações tenha dados válidos e não fique travada
    if df_o.empty or len(df_o) == 0:
        dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
        df_o = pd.DataFrame({"Data": dias_v, "Observacao": [""]*7})
    
    # Força a conversão para texto para evitar bloqueios de digitação no editor
    df_o["Observacao"] = df_o["Observacao"].astype(str).replace("nan", "")

    st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
    
    # Configuração correta para permitir a edição livre da coluna de texto
    obs_edit = st.data_editor(
        df_o, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Data": st.column_config.TextColumn("Data", disabled=True),
            "Observacao": st.column_config.TextColumn("Observação", disabled=False, required=False)
        }
    )
    
    if st.button("Salvar Observações"):
        rp.update_file("observacoes.csv", "Update", obs_edit.to_csv(index=False), f_o.sha)
        st.success("Observações salvas com sucesso."); st.rerun()

    st.markdown("---")
    
    # --- FILTRO POR PASSAGEIRO ---
    st.write("### Filtrar Programação")
    passageiro_filtro = st.text_input("Digite o nome do passageiro para filtrar (Deixe em branco para ver todos):").strip().upper()

    # Aplica o filtro se o usuário digitou algo
    if passageiro_filtro:
        df_filtrado = df_v[df_v['Passageiro'].astype(str).str.contains(passageiro_filtro, na=False)]
    else:
        df_filtrado = df_v

    # --- BOTÃO PARA SALVAR EM PDF / IMPRIMIR ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <script>
        function imprimirJanela() {
            window.print();
        }
        </script>
    """, unsafe_allow_html=True)
    
    # Botão com truque JavaScript nativo para disparar a impressão da página limpa
    if st.button("🖨️ Gerar PDF / Imprimir Agenda", use_container_width=True):
        st.components.v1.html("<script>window.print();</script>", height=0, width=0)
        st.info("Se a janela de impressão não abrir automaticamente, utilize o atalho Ctrl + P (ou Cmd + P no Mac) no seu teclado.")

    # Trecho 1: Pontes e Lacerda x Cuiabá
    st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
    df_pl = df_filtrado[df_filtrado['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
    cols_pl = ["Passageiro", "semana", "data", "horário", "saída", "Cia/nº voo", "Horário do Voo", "Data do Voo", "Hotel em Cuiabá", "Motorista"]
    for c in cols_pl:
        if c not in df_pl.columns: df_pl[c] = ""
    st.dataframe(df_pl[cols_pl], use_container_width=True, hide_index=True)

    # Trecho 2: Cuiabá x Pontes e Lacerda
    st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
    df_cp = df_filtrado[df_filtrado['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
    cols_cp = ["Passageiro", "semana", "data", "horário", "Cia/nº voo", "Hotel Cuiabá", "semana_ret", "data_ret", "horário_ret", "Motorista", "Hospedagem . Lacerda"]
    for c in cols_cp:
        if c not in df_cp.columns: df_cp[c] = ""
    st.dataframe(df_cp[cols_cp], use_container_width=True, hide_index=True)

    # Trecho 3: Outros Trajetos e Cidades
    st.markdown('<br><div class="trecho-header">OUTROS TRAJETOS E CIDADES (VIAGENS ESPECIAIS)</div>', unsafe_allow_html=True)
    df_outros = df_filtrado[~df_filtrado['Trajeto'].isin(["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda"])]
    cols_outros = ["Passageiro", "Trajeto", "semana", "data", "horário", "saída", "Motorista", "Hotel em Cuiabá"]
    for c in cols_outros:
        if c not in df_outros.columns: df_outros[c] = ""
    st.dataframe(df_outros[cols_outros], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro na conexão com o banco de dados: {e}")
