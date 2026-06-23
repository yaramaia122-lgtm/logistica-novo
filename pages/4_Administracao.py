import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.session_state['logado'] = False; st.switch_page("main.py")

st.set_page_config(page_title="Administração - AURA", layout="wide")
st.title("🎛️ Painel Administrativo de Logística")

st.write("### 📝 Editar Informações de Viagens e Custos Salvos na Base")

tk, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
f_file = rp = Github(auth=Auth.Token(tk)).get_repo(repo).get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_file.decoded_content.decode()))

# 📝 FORMULÁRIO DE ATUALIZAÇÃO REESTRUTURADO
st.write("---")
st.write("### ✏️ Inserir ou Alterar Registro Manualmente")

col_p, col_m, col_d = st.columns(3)
p_nome = col_p.text_input("Nome do Passageiro:")
# LISTA SUSPENSA PARA MOTORISTAS
m_nome = col_m.selectbox("Selecione o Motorista:", ["Ilson", "Outro Motorista", "Particular"])
# CALENDÁRIO PADRÃO BRASILEIRO NATIVO
d_viagem = col_d.date_input("Data da Viagem (DD/MM/YYYY):", datetime.now())

col_t, col_s, col_h = st.columns(3)
# LISTA SUSPENSA PARA TRAJETOS
t_escolha = col_t.selectbox("Trajeto da Viagem:", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outros"])
# LISTA SUSPENSA PARA STATUS
s_escolha = col_s.selectbox("Status Atual:", ["Confirmado", "Cancelado", "Ocultado"])
h_saida = col_h.text_input("Horário de Saída (HH:MM):")

st.write("#### 💰 Custos Associados")
c1, c2, c3, c4 = st.columns(4)
v_hotel = c1.text_input("Custo Hotel (R$):", "0.00")
v_comb = c2.text_input("Custo Transfer/Combustível (R$):", "0.00")
v_aereo = c3.text_input("Custo Aéreo (R$):", "0.00")
v_outros = c4.text_input("Outros Custos (R$):", "0.00")

if st.button("💾 Adicionar / Atualizar Registro na Base", width='stretch'):
    if not p_nome:
        st.error("Por favor, informe o nome do passageiro.")
    else:
        v_total = float(v_hotel) + float(v_comb) + float(v_aereo) + float(v_outros)
        novo_reg = {
            "passageiro": p_nome.strip(), "motorista": m_nome, "data": d_viagem.strftime('%d/%m/%Y'),
            "hora_saida": h_saida, "trajeto": t_escolha, "status": s_escolha,
            "centro_custo": "210301 - Moagem", "hotel_v": v_hotel, "comb_v": v_comb,
            "aereo_v": v_aereo, "outros_v": v_outros, "total": str(v_total), "voo": ""
        }
        df_v = pd.concat([df_v, pd.DataFrame([novo_reg])], ignore_index=True)
        Github(auth=Auth.Token(tk)).get_repo(repo).update_file("dados_logistica.csv", "Admin Update", df_v.to_csv(index=False), f_file.sha)
        st.success("Base de dados atualizada!"); st.rerun()

st.write("### 🔍 Visualização Geral da Planilha de Custos")
cfg_admin = {"passageiro": "Passageiro", "motorista": "Motorista", "data": "Data"}
st.data_editor(df_v, hide_index=True, width='stretch', key="editor_admin_v1")
