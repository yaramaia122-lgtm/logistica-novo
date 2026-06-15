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

# Campos de preenchimento fora do modo form estático para permitir a atualização dinâmica da tela
passageiro = st.text_input("Nome do Passageiro:")
trajeto = st.selectbox("Selecione o Trajeto:", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros"])

# 🔄 INTERFACE INTELIGENTE: O campo abaixo só existe se "Outros" for selecionado
trajeto_custom = ""
if trajeto == "Outros":
    trajeto_custom = st.text_input("Digite qual é o trajeto personalizado:")

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

st.markdown("---")
enviar = st.button("Gravar e Sincronizar Programação", use_container_width=True)

if enviar:
    if not passageiro.strip():
        st.error("Por favor, preencha o nome do passageiro.")
    elif trajeto == "Outros" and not trajeto_custom.strip():
        st.error("Por favor, especifique o trajeto personalizado no campo que apareceu.")
    else:
        try:
            tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
            rp = Github(auth=Auth.Token(tk)).get_repo(repo)
            
            file_content = rp.get_contents("dados_logistica.csv")
            df_atual = pd.read_csv(io.StringIO(file_content.decoded_content.decode()))
            
            trajeto_final = trajeto_custom.strip() if trajeto == "Outros" else trajeto
            semana_calculada = dias_traduzidos[data_viagem.weekday()]
            
            nova_viagem = {
                "passageiro": passageiro.strip(),
                "trajeto": trajeto_final.strip(),
                "semana": semana_calculada,
                "data": data_viagem.strftime('%d/%m/%Y'),
                "horário": horario.strip(),
                "saída": saida_local.strip(),
                "cia/nº voo": cia_voo.strip(),
                "horário do voo": horario_voo.strip(),
                "data do voo": data_voo.strftime('%d/%m/%Y') if data_voo else "",
                "hotel em cuiabá": hotel_cuiaba.strip(),
                "hospedagem em p. lacerda": hospedagem_lacerda.strip(),
                "hotel (r$)": c_hotel.strip(),
                "aéreo (r$)": c_aereo.strip(),
                "transfer (r$)": c_transfer.strip(),
                "outros (r$)": c_outros.strip(),
                "motorista": motorista.strip()
            }
            
            df_nova = pd.DataFrame([nova_viagem])
            df_final = pd.concat([df_atual, df_nova], ignore_index=True)
            
            rp.update_file("dados_logistica.csv", "Nova viagem cadastrada", df_final.to_csv(index=False), file_content.sha)
            st.success("Sucesso! Registro salvo e sincronizado.")
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro ao salvar no banco de dados: {e}")
