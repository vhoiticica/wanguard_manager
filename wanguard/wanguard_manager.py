import streamlit as st
import yaml

#-----------------------------CARREGAR ARQUIVO DE CONFIGURAÇÃO-----------------------------#

def carregar_configuracoes(caminho_arquivo):
    with open(caminho_arquivo, 'r') as file:
        configuracoes = yaml.safe_load(file)
    return configuracoes

config = carregar_configuracoes(r"../config/config.yaml")

#-----------------------------PAGINA DE LOGIN-----------------------------#
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def verificar_credenciais(username, password):
    for server_name, server_data in config.items():
        if username == server_data['username'] and password == server_data['password']:
            return True  
    return False

def login():
    st.title("Página de Login")

    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    
    
    if st.button("Logar"):
        if verificar_credenciais(username, password):
            st.session_state.logged_in = True
            st.success("Login bem-sucedido!")
            st.rerun()  
        else:
            st.session_state.logged_in = False
            st.error("Credenciais incorretas. Tente novamente.")

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

#-----------------------------MAIN-----------------------------#

if st.session_state.logged_in:

    main_page = st.Page(
            "main_page.py", title="Arquivo de Configuração", default=True
        )

    #-----------------------------SERVER1-----------------------------#
    if 'Server1' in config:
        server1 = config['Server1']
        remove_srv1 = st.Page(
            "../servers/server1/remove_duplicates_srv1.py", title=f"{server1['name']} - Remover Duplicados"
        )
        anuncio_srv1 = st.Page(
            "../servers/server1/anuncio_bgp_srv1.py", title=f"{server1['name']} - Anúncio BGP"
        )

    #-----------------------------SERVER2-----------------------------#
    if 'Server2' in config:
        server2 = config['Server2']
        remove_srv2 = st.Page(
            "../servers/server2/remove_duplicates_srv2.py", title=f"{server2['name']} - Remover Duplicados"
        )
        anuncio_srv2 = st.Page(
            "../servers/server2/anuncio_bgp_srv2.py", title=f"{server2['name']} - Anúncio BGP"
        )

    #-----------------------------BARRA LATERAL-----------------------------#
    pg = st.navigation({
        f"{server1['name'].upper()}": [anuncio_srv1, remove_srv1],
        f"{server2['name'].upper()}": [anuncio_srv2, remove_srv2],
        "Configurações": [main_page],
        "Account": [logout_page],
    })

    pg.run()

else:
    login()
