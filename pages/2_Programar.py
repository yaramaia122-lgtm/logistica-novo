import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime
import zoneinfo

# 1. VERIFICAÇÃO DE LOGIN DE USUÁRIO
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Programar - AURA LOGISTICS", layout="wide")

# 🎨 ESTILIZAÇÃO CORPORATIVA PROFISSIONAL (SEM EMOJIS)
st.markdown("""<style>
    .stApp { background-color: #F8FAFC !important; }
    .main-title { color: #002D5E !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }
    .subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }
    .section-header { background-color: #002D5E !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }
    .subsection-header { color: #002D5E !important; font-weight: bold; font-size: 11pt; margin-top: 15px; margin-bottom: 10px; border-left: 4px solid #FF7F50; padding-left: 8px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Planejamento e Programação de Viagens</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Abertura de ordens de transporte, alocação de passageiros e provisionamento logístico inicial</div>', unsafe_allow_html=True)

# 2. CONEXÃO SEGURA COM O REPOSITÓRIO GITHUB
tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))

# 3. CAPTURA AUTOMÁTICA DE DATAS E FUSO OPERACIONAL
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje = datetime.now(fuso)
data_hoje = hoje.date()

# 4. FORMULÁRIO OPERACIONAL DIVIDIDO EM SEÇÕES
st.markdown('<div class="section-header">Dados Cadastrais Básicos</div>', unsafe_allow_html=True)

col_p, col_m, col_d = st.columns(3)
p_nome = col_p.text_input("Nome do Passageiro")
m_nome = col_m.selectbox("Motorista Designado", ["Ilson", "Particular", "Outro Profissional"])
d_viagem = col_d.date_input("Data da Viagem", data_hoje)

col_t, col_h, col_s = st.columns(3)
t_escolha = col_t.selectbox("Trajeto Obrigatório", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros"])
h_saida = col_h.text_input("Horário Estimado de Saída (HH:MM)")
s_semana = col_s.selectbox("Dia da Semana Correspondente", ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"])

# SEÇÃO DE PROVISIONAMENTO DE VOOS
st.markdown('<div class="section-header">Provisionamento de Transporte Aéreo</div>', unsafe_allow_html=True)
c_voo = st.checkbox("Esta programação envolve trecho com passagem aérea aérea?")

v_cia, v_horario, v_data = "", "", ""
if c_voo:
    col_a1, col_a2, col_a3 = st.columns(3)
    v_cia = col_a1.text_input("Companhia e Número do Voo")
    v_horario = col_a2.text_input("Horário do Voo (HH:MM)")
    v_data_input = col_a3.date_input("Data do Voo", data_hoje)
    v_data = v_data_input.strftime('%d/%m/%Y')

# SEÇÃO DE PROVISIONAMENTO DE HOSPEDAGENS
st.markdown('<div class="section-header">Provisionamento de Hospedagem</div>', unsafe_allow_html=True)
c_hotel = st.checkbox("Esta programação exige reserva de hotel em Cuiabá?")

h_nome = ""
if c_hotel:
    h_nome = st.text_input("Nome do Estabelecimento / Hotel indicado")

st.markdown("---")

# 5. PROCESSAMENTO E PERSISTÊNCIA DOS DADOS NO GITHUB
if st.button("Consolidar e Registrar Programação", width='stretch'):
    if not p_nome.strip():
        st.error("Erro: O preenchimento do nome do passageiro é obrigatório para prosseguir.")
    else:
        # Padroniza as colunas da planilha para letras minúsculas estruturadas
        df_v.columns = df_v.columns.str.strip().str.lower()
        df_v.columns = df_v.columns.str.replace("á", "a").str.replace("í", "i").str.replace("º", "")
        df_v = df_v.loc[:, ~df_v.columns.duplicated()]

        # Criação do registro limpo e estruturado
        novo_registro = {
            "passageiro": p_nome.strip(),
            "motorista": m_nome,
            "semana": s_semana,
            "data": d_viagem.strftime('%d/%m/%Y'),
            "horario": h_saida.strip(),
            "saida": "Logística",
            "trajeto": t_escolha,
            "cia/n voo": v_cia.strip(),
            "horario do vuo": v_horario.strip(),
            "data do vuo": v_data,
            "hotel em cuiaba": h_nome.strip(),
            "status": "Confirmado",
            "centro_custo": "210301 - Moagem",
            "hotel_v": "0.00",
            "comb_v": "0.00",
            "aereo_v": "0.00",
            "outros_v": "0.00",
            "total": "0.00",
            "voo": ""
        }

        # Concatena e atualiza diretamente no repositório GitHub de forma limpa
        df_final = pd.concat([df_v, pd.DataFrame([novo_registro])], ignore_index=True)
        rp.update_file("dados_logistica.csv", "New Trip Reservation Entry via Programar", df_final.to_csv(index=False), f_log.sha)
        st.success("Programação registrada com sucesso na base de dados corporativa."); st.rerun()

st.markdown("---")

# 6. HISTÓRICO RECENTE EM MODO DE LEITURA
st.markdown('<div class="subsection-header">Últimas Programações Registradas em Sistema</div>', unsafe_allow_html=True)
df_v_display = df_v.copy()
df_v_display.columns = df_v_display.columns.str.upper()
st.dataframe(df_v_display.tail(10), width='stretch', hide_index=True)
