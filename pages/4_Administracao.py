import streamlit as st
import pandas as pd
from github import Github, Auth
import io

st.set_page_config(page_title="Login - AURA LOGISTICS", layout="centered")

# CSS para a interface de login
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; }
    .login-title {
        color: #1b294b;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if st.session_state['logado']:
    st.switch_page("pages/1_Agenda.py")

st.markdown('<h2 class="login-title">🔒 AURA LOGISTICS - Controle de Acesso</h2>', unsafe_allow_html=True)

with st.container():
    with st.form("login_form"):
        usuario = st.text_input("Usuário:").strip()
        senha = st.text_input("Senha:", type="password").strip()
        enviar = st.form_submit_button("Entrar no Sistema", use_container_width=True)

        if enviar:
            # 🌟 REGRA MESTRE: Libera o acesso imediato e corrige o ficheiro corrompido no GitHub
            if usuario == "adm" and senha == "aura123":
                st.session_state['logado'] = True
                
                try:
                    tk = st.secrets["GITHUB_TOKEN"]
                    repo = st.secrets["GITHUB_REPO"]
                    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
                    
                    df_base_u = pd.DataFrame([{"usuario": "adm", "senha": "aura123"}])
                    try:
                        f_user = rp.get_contents("usuarios.csv")
                        rp.update_file("usuarios.csv", "Restauracao Mestre de Credenciais", df_base_u.to_csv(index=False), f_user.sha)
                    except Exception:
                        rp.create_file("usuarios.csv", "Inicializar tabela de usuarios", df_base_u.to_csv(index=False))
                except Exception:
                    pass
                
                st.success("Acesso mestre concedido! Redirecionando...")
                st.rerun()
            else:
                # Validação normal para os outros utilizadores cadastrados
                try:
                    tk = st.secrets["GITHUB_TOKEN"]
                    repo = st.secrets["GITHUB_REPO"]
                    rp = Github(auth=Auth.Token(tk)).get_repo(repo)
                    f_user = rp.get_contents("usuarios.csv")
                    df_u = pd.read_csv(io.StringIO(f_user.decoded_content.decode()))
                    df_u.columns = df_u.columns.str.strip().str.lower()
                    
                    validou = False
                    for _, row in df_u.iterrows():
                        if str(row['usuario']).strip() == usuario and str(row['senha']).strip() == senha:
                            validou = True
                            break
                    
                    if validou:
                        st.session_state['logado'] = True
                        st.success("Login efetuado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
                except Exception:
                    st.error("Erro na base de dados de utilizadores. Utilize as credenciais mestre para restaurar.")
