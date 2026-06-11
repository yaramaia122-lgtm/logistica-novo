import streamlit st
import pandas as pd
from github import Github, Auth
import io

if 'logado' not in st.session_state or not st.session_state['logado']: st.stop()

st.set_page_config(page_title="Programar - AURA", layout="wide")

with st.sidebar:
    st.markdown("---")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['user'] = None
        st.rerun()

CC_LISTA = [
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manutenção Mecânica Planta",
    "210405 - Lixiviação / Cianetação", "210101 - Administração Planta", "211001 - Manutencao Eletrica Planta",
    "211003 - Oficina Manutenção Planta", "210201 - Britagem Primária", "210604 - Fundição", "310101 - Almoxarifado",
    "320401 - Controladoria e Contabilidade", "310701 - Serviços Gerais", "320601 - Celula de Gestao de Contratos",
    "320101 - Suprimentos", "320502 - Tecnologia da Informação", "311202 - Care and Maintenance SF",
    "330102 - Apoena Corporativo", "311203 - Care and Maintenance PPQ", "340103 - Jurídico",
    "310801 - Segurança Patrimonial", "310301 - PCP", "320201 - Gerência Geral", "310508 - Comunidades",
    "320303 - Trainee", "320301 - Recursos Humanos", "310902 - Campo", "310904 - Exploração EPP",
    "121101 - Geologia Operacional - Mina Ernesto", "121102 - Planejamento e Topografia Operacional - Mina Ernes",
    "151101 - Geologia Operacional - Mina Nosde", "151103 - Geotecnia - Nosde", "210502 - Barragem",
    "151102 - Planejamento e Topografia Operacional - Mina Nosde", "310501 - Meio Ambiente",
    "310503 - Segurança do Trabalho", "310502 - Saude", "150101 - Administração de Mina - Céu Aberto - Nosde",
    "120101 - Administração de Mina - Céu Aberto - Ernesto"
]

tk = st.secrets["GITHUB_TOKEN"]
rp = Github(auth=Auth.Token(tk)).get_repo(st.secrets["GITHUB_REPO"])
f_v = rp.get_contents("dados_logistica.csv")
df_v = pd.read_csv(io.StringIO(f_v.decoded_content.decode()))

with st.form("programar_viagem"):
    c1, c2 = st.columns(2)
    px = c1.text_input("Passageiro").upper()
    mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "A definir", "Outro"])
    
    # ADICIONADO A OPÇÃO FLEXÍVEL DE SELEÇÃO DE TRAJETO
    tj_selecao = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Outras Cidades (Especificar abaixo)"])
    tj_custom = c1.text_input("Se selecionou 'Outras Cidades', especifique o trajeto (Ex: Lacerda x Vila Bela):").strip()
    
    cc = c1.selectbox("Centro de Custo", CC_LISTA)
    
    dt = c2.date_input("Data")
    sem = c2.selectbox("Dia da Semana", ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"])
    hs = c2.text_input("Hora Saída")
    ht = c2.text_input("Hotel/Destino Final")
    vn = c1.text_input("Cia/nº voo (Se houver)")
    vh = c2.text_input("Horário do Voo (Se houver)")
    
    st.markdown("### Custos (Acesso Restrito)")
    f1, f2, f3, f4 = st.columns(4)
    c_h = f1.number_input("Custo Hotel", 0.0)
    c_c = f2.number_input("Custo Combustível", 0.0)
    c_a = f3.number_input("Custo Aéreo", 0.0)
    c_o = f4.number_input("Outros Custos", 0.0)
    
    if st.form_submit_button("CONFIRMAR E ENVIAR PARA AGENDA"):
        # Validação do trecho customizado
        trajeto_final = tj_custom if tj_selecao == "Outras Cidades (Especificar abaixo)" and tj_custom != "" else tj_selecao
        
        total = c_h + c_c + c_a + c_o
        nova = pd.DataFrame([{
            "Passageiro": px, "Motorista": mt, "Trajeto": trajeto_final, "Centro_Custo": cc,
            "semana": sem, "data": dt.strftime('%d/%m'), "horário": hs, "saída": ht,
            "Cia/nº voo": vn, "Horário do Voo": vh, "Data do Voo": dt.strftime('%d/%m'),
            "Hotel em Cuiabá": ht, "Hotel Cuiabá": ht, "semana_ret": sem, "data_ret": dt.strftime('%d/%m'),
            "horário_ret": hs, "Hospedagem . Lacerda": ht,
            "Hotel_V": c_h, "Comb_V": c_c, "Aereo_V": c_a, "Outros_V": c_o, "Total": total, "Status": "Confirmada"
        }])
        df_f = pd.concat([df_v, nova], ignore_index=True)
        rp.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), f_v.sha)
        st.success("Logística integrada na Agenda com sucesso."); st.rerun()
