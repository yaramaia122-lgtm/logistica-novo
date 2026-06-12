import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False
    st.switch_page("main.py")

st.set_page_config(page_title="Programar - AURA", layout="wide")

st.title("📝 Programar Nova Viagem de Logística")

# Dicionário de tradução para automação da semana
dias_traduzidos = {
    0: "Segunda-Feira", 1: "Terça-Feira", 2: "Quarta-Feira",
    3: "Quinta-Feira", 4: "Sexta-Feira", 5: "Sábado", 6: "Domingo"
}

with st.form("form_logistica", clear_on_submit=True):
    passageiro = st.text_input("Nome do Passageiro:")
    trajeto = st.selectbox("Selecione o Trajeto:", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros"])
    trajeto_custom = st.text_input("Se escolheu 'Outros', digite o trajeto:") if trajeto == "Outros" else ""
    
    data_viagem = st.date_input("Data da Viagem:", datetime.now())
    horario = st.text_input("Horário de Saída/Encontro (Ex: 08:00):")
    saida_local = st.text_input("Local de Saída (Se aplicável):")
    
    st.markdown("---")
    st.write("### ✈️ Informações Adicionais de Voo / Hospedagem")
    cia_voo = st.text_input("Cia / Nº do Voo:")
    horario_voo = st.text_input("Horário do Voo:")
    data_voo = st.date_input("Data do Voo (Se diferente):", value=None, json_encoder=None)
    
    hotel_cuiaba = st.text_input("Hotel em Cuiabá (Se aplicável):")
    hospedagem_lacerda = st.text_input("Hospedagem em P. Lacerda (Se aplicável):")
    motorista = st.text_input("Nome do Motorista Designado:")
    
    enviar = st.form_submit_button("💾 Gravar e Sincronizar Programação", use_container_width=True)

if enviar:
    if not passageiro.strip():
        st.error("Por favor, preencha o nome do passageiro.")
    else:
        try:
            tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
            rp = Github(auth=Auth.Token(tk)).get_repo(repo)
            
            # Puxa o arquivo atual do GitHub
            file_content = rp.get_contents("dados_logistica.csv")
            df_atual = pd.read_csv(io.StringIO(file_content.decoded_content.decode()))
            
            # 🛡️ TRATAMENTO INTELIGENTE DA DATA E SEMANA (Sincronização Ativa)
            trajeto_final = trajeto_custom.strip() if trajeto == "Outros" else trajeto
            semana_calculada = dias_traduzidos[data_viagem.weekday()]
            data_viagem_br = data_viagem.strftime('%d/%m/%Y')
            data_voo_br = data_voo.strftime('%d/%m/%Y') if data_voo else ""
            
            # Montagem da nova linha alinhada rigorosamente em minúsculas
            nova_viagem = {
                "passageiro": passageiro.strip(),
                "trajeto": trajeto_final.strip(),
                "semana": semana_calculada,
                "data": data_viagem_br,
                "horário": horario.strip(),
                "saída": saida_local.strip(),
                "cia/nº voo": cia_voo.strip(),
                "horário do voo": horario_voo.strip(),
                "data do voo": data_voo_br,
                "hotel em cuiabá": hotel_cuiaba.strip(),
                "hotel cuiabá": hotel_cuiaba.strip(), # Compatibilidade dupla
                "motorista": motorista.strip(),
                "hospedagem . lacerda": hospedagem_lacerda.strip()
            }
            
            df_nova = pd.DataFrame([nova_viagem])
            df_final = pd.concat([df_atual, df_nova], ignore_index=True)
            
            # Devolve o arquivo atualizado e higienizado para o repositório
            rp.update_file("dados_logistica.csv", "Nova viagem adicionada", df_final.to_csv(index=False), file_content.sha)
            st.success(f"Sucesso! Viagem de {passageiro} programada para {semana_calculada} ({data_viagem_br}) gravada com êxito.")
            
        except Exception as e:
            st.error(f"Erro ao salvar no banco de dados: {e}")
