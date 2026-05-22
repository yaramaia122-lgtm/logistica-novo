import streamlit as st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.stop()

st.set_page_config(page_title="Programar - AURA", layout="wide")

CC_LISTA = ["210301-Moagem", "210401-Planta", "310101-RH/Adm", "320201-Gerencia", "121101-Geologia", "150101-Mina"]

tk = st.secrets["GITHUB_TOKEN"]
rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])
f_v = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))

with st.form("programar_viagem"):
    c1, c2 = st.columns(2)
    px = c1.text_input("Passageiro").upper()
    mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
    tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
    cc = c1.selectbox("Centro de Custo", CC_LISTA)
    
    dt = c2.date_input("Data")
    hs = c2.text_input("Hora Saída")
    ht = c2.text_input("Hotel/Destino")
    vn = c1.text_input("Voo Nº")
    vh = c2.text_input("Hora Voo")
    
    st.markdown("### 💰 Custos Ocultos (Administrativo)")
    f1, f2, f3, f4 = st.columns(4)
    c_h = f1.number_input("Custo Hotel", 0.0)
    c_c = f2.number_input("Custo Comb.", 0.0)
    c_a = f3.number_input("Custo Aéreo", 0.0)
    c_o = f4.number_input("Outros Custos", 0.0)
    
    if st.form_submit_button("💥 AGENDAR E INTEGRAR COM A AGENDA"):
        total = c_h + c_c + c_a + c_o
        nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Hora_Saida":hs,"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Hotel_V":c_h,"Comb_V":c_c,"Aereo_V":c_a,"Outros_V":c_o,"Total":total,"Voo":vn,"Voo_Hora":vh,"Hotel":ht}])
        df_f = pd.concat([df_v, nova], ignore_index=True)
        rp.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), f_v.sha)
        st.success("Viagem adicionada com sucesso!"); st.rerun()
