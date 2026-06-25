import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime
import zoneinfo

# 1. VERIFICAÇÃO DE LOGIN
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Programar Transporte - AURA LOGISTICS", layout="wide")

# CSS DA TELA (SEGURO CONTRA ERROS DO PYTHON 3.14)
css_tela = "<style>"
css_tela += ".stApp { background-color: #F8FAFC !important; }"
css_tela += ".main-title { color: #1b294b !important; font-size: 24pt !important; font-weight: bold; margin-bottom: 5px; }"
css_tela += ".subtitle { color: #64748B !important; font-size: 11pt !important; margin-bottom: 25px; }"
css_tela += ".section-header { background-color: #1b294b !important; color: white !important; padding: 8px 15px; font-weight: bold; font-size: 12pt; border-radius: 4px; margin-top: 15px; margin-bottom: 15px; }"
css_tela += "</style>"
st.markdown(css_tela, unsafe_allow_html=True)

st.markdown('<div class="main-title">Programar Novo Transporte</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Insira os dados da viagem. O sistema definirá o dia da semana automaticamente.</div>', unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
tk = st.secrets["GITHUB_TOKEN"]
repo = st.secrets["GITHUB_REPO"]
rp = Github(auth=Auth.Token(tk)).get_repo(repo)

f_log = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_log.decoded_content.decode()))

# Lista de dias da semana para cálculo automático
dias_semana_pt = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
fuso = zoneinfo.ZoneInfo("America/Cuiaba")
hoje = datetime.now(fuso).date()

# 3. FORMULÁRIO DE CADASTRO
st.markdown('<div class="section-header">Informações Gerais e de Faturamento</div>', unsafe_allow_html=True)

col_geral1, col_geral2 = st.columns(2)
with col_geral1:
    passageiro = st.text_input("Nome do Passageiro:", key="prog_passageiro").strip()
    trajeto = st.selectbox("Selecione o Trajeto:", [
        "Pontes e Lacerda x Cuiabá", 
        "Cuiabá x Pontes e Lacerda", 
        "Outros Trajetos / Viagem Especial"
    ])

with col_geral2:
    # O Centro de Custo é obrigatório aqui, mas a Agenda já está programada para ocultá-lo da visão geral
    centro_custo = st.text_input("Centro de Custo (Oculto na Agenda):", key="prog_cc").strip()
    motorista = st.text_input("Motorista Designado:", key="prog_motorista").strip()

# Formulários dinâmicos baseados no Trajeto selecionado
if trajeto == "Pontes e Lacerda x Cuiabá":
    st.markdown('<div class="section-header">Logística: Saída de Pontes e Lacerda para Cuiabá</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        data_ida = st.date_input("Data da Saída:", value=hoje, key="pl_data")
        horario_ida = st.text_input("Horário da Saída (Ex: 06:00):", key="pl_hora")
    with col2:
        saida_loc = st.text_input("Local de Saída/Embarque:", key="pl_saida")
        destino_loc = st.text_input("Destino Final em Cuiabá (Hotel/Aeroporto):", key="pl_destino")
    with col3:
        voo_num = st.text_input("Cia / Nº do Voo (Se houver):", key="pl_voo")
        voo_hora = st.text_input("Horário do Voo (Se houver):", key="pl_voo_hora")
        voo_data = st.date_input("Data do Voo (Se houver):", value=hoje, key="pl_voo_data")

    # Automação do Dia da Semana
    dia_semana_calculado = dias_semana_pt[data_ida.weekday()]
    st.caption("📅 Dia da semana detectado automaticamente: **" + dia_semana_calculado + "**")

elif trajeto == "Cuiabá x Pontes e Lacerda":
    st.markdown('<div class="section-header">Logística: Chegada em Cuiabá e Retorno para Pontes e Lacerda</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        data_ret = st.date_input("Data da Chegada do Voo:", value=hoje, key="cp_data_ret")
        horario_ret = st.text_input("Horário de Chegada do Voo (Ex: 14:30):", key="cp_hora_ret")
        voo_num = st.text_input("Cia / Nº do Voo:", key="cp_voo")
    with col2:
        hotel_cuiaba = st.text_input("Hotel em Cuiabá (Se houver):", key="cp_hotel")
        data_ida = st.date_input("Data da Saída para P. Lacerda:", value=hoje, key="cp_data_saida")
        horario_ida = st.text_input("Horário da Saída para P. Lacerda:", key="cp_hora_saida")
    with col3:
        destino_loc = st.text_input("Destino Final em P. Lacerda (Residência/Obra):", key="cp_destino")
        saida_loc = "Aeroporto/Hotel Cuiabá"
        voo_hora = ""
        voo_data = hoje

    # Automação do Dia da Semana para Ida e Retorno
    dia_semana_calculado = dias_semana_pt[data_ida.weekday()]
    dia_semana_ret_calculado = dias_semana_pt[data_ret.weekday()]
    st.caption("📅 Dia de Saída p/ PL: **" + dia_semana_calculado + "** | Dia de Chegada do Voo: **" + dia_semana_ret_calculado + "**")

else:
    st.markdown('<div class="section-header">Logística: Viagem Especial / Outros Trajetos</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        data_ida = st.date_input("Data da Viagem:", value=hoje, key="out_data")
        horario_ida = st.text_input("Horário:", key="out_hora")
        saida_loc = st.text_input("Origem/Saída:", key="out_saida")
    with col2:
        destino_loc = st.text_input("Destino Final:", key="out_destino")
        voo_num = st.text_input("Voo / Informações Extras:", key="out_voo")
        voo_hora = ""
        voo_data = hoje

    dia_semana_calculado = dias_semana_pt[data_ida.weekday()]
    st.caption("📅 Dia da semana detectado automaticamente: **" + dia_semana_calculado + "**")

st.markdown("---")

# 4. SALVAMENTO DOS DADOS ALINHADO COM A AGENDA
if st.button("🚀 Confirmar e Programar Transporte", width='stretch'):
    if not passageiro:
        st.error("Por favor, preencha o nome do Passageiro.")
    else:
        # Cria a nova linha mapeando exatamente os nomes das colunas que a base possui
        nova_linha = {
            "centro_custo": centro_custo,
            "passageiro": passageiro,
            "trajeto": trajeto.lower(), # Salva em minúsculo para bater com os filtros da agenda
            "status": "Confirmado",
            "motorista": motorista,
            "semana": dias_semana_pt[data_ida.weekday()],
            "data": data_ida.strftime('%d/%m/%Y'),
            "horario": horario_ida,
            "saida": saida_loc,
            "destino": destino_loc,
            "cia/n voo": voo_num,
            "horario do voo": voo_hora,
            "data do voo": voo_data.strftime('%d/%m/%Y') if isinstance(voo_data, datetime) or hasattr(voo_data, 'strftime') else ""
        }
        
        # Se for o trecho de Cuiabá, alimenta os campos específicos de retorno também
        if trajeto == "Cuiabá x Pontes e Lacerda":
            nova_linha["semana_ret"] = dias_semana_pt[data_ret.weekday()]
            nova_linha["data_ret"] = data_ret.strftime('%d/%m/%Y')
            nova_linha["horario_ret"] = horario_ret
            nova_linha["hotel cuiaba"] = hotel_cuiaba

        # Converte para DataFrame e faz o Append seguro na base existente
        df_nova_row = pd.DataFrame([nova_linha])
        df_final_salvar = pd.concat([df_v, df_nova_row], ignore_index=True)
        
        # Envia de volta para o GitHub
        conteudo_csv = df_final_salvar.to_csv(index=False)
        rp.update_file("dados_logistica.csv", "Nova Programacao Automatizada", conteudo_csv, f_log.sha)
        
        st.success("Transporte de " + passageiro + " programado e sincronizado com sucesso!")
        st.balloons()
