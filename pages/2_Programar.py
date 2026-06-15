import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False; st.switch_page("main.py")

st.set_page_config(page_title="Programar - AURA", layout="wide")

st.title("Programar Nova Viagem de Logística")

dias_traduzidos = {
    0: "Segunda-Feira", 1: "Terça-Feira", 2: "Quarta-Feira",
    3: "Quinta-Feira", 4: "Sexta-Feira", 5: "Sábado", 6: "Domingo"
}

with st.form("form_logistica", clear_on_submit=True):
    passageiro = st.text_input("Nome do Passageiro:")
    trajeto = st.selectbox("Selecione o Trajeto:", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros"])
    trajeto_custom = st.text_input("Se escolheu 'Outros', digite o trajeto:") if trajeto == "Outros" else ""
    
    st.write("### Informações da Viagem")
    data_viagem = st.date_input("Data da Viagem:", datetime.now())
    horario = st.text_input("Horário de Saída/Chegada:")
    saida_local = st.text_input("Local de Saída (Se aplicável):")
    
    st.write("### Logística de Voo / Hospedagem")
    cia_voo = st.text_input("Cia / Nº do Voo:")
    horario_voo = st.text_input("Horário do Voo:")
    data_voo = st.date_input("Data do Voo:", value=None)
    hotel_cuiaba = st.text_input("Hotel em Cuiabá (Se houver):")
    hospedagem_lacerda = st.text_input("Hospedagem em P. Lacerda (Se houver):")
    motorista = st.text_input("Nome do Motorista Designado:")
    
    st.write("### Detalhamento Financeiro (Apenas para o Dashboard)")
    c1, c2, c3, c4 = st.columns(4)
    c_hotel = c1.text_input("Hotel (R$):", value="0.00")
    c_aereo = c2.text_input("Aéreo (R$):", value="0.00")
    c_transfer = c3.text_input("Transfer (R$):", value="0.00")
    c_outros = c4.text_input("Outros Custos (R$):", value="0.00")
    
    en
