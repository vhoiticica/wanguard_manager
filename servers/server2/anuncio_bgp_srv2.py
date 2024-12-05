import streamlit as st
import requests
import base64
import ipaddress
from collections import defaultdict
import yaml

# Função para carregar configurações do arquivo YAML
def carregar_configuracoes(caminho_arquivo):
    with open(caminho_arquivo, 'r') as file:
        configuracoes = yaml.safe_load(file)
    return configuracoes

# Carregar as configurações do arquivo YAML
config = carregar_configuracoes("config.yaml")

# Obter as configurações do servidor escolhido
servidor = config['Server2']
USERNAME = servidor['username']
PASSWORD = servidor['password']
API_BASE_URL = servidor['api_base_url']

#-----------------------------FUNÇÕES GLOBAIS-----------------------------#

def get_ip_zones():
    url = f"{API_BASE_URL}/ip_zones/1/prefixes"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        data = response.json()
        prefixos_dict = {}
        for item in data:
            grupo = item['ip_group']
            prefixo = item['prefix']
            if grupo not in prefixos_dict:
                prefixos_dict[grupo] = []
            prefixos_dict[grupo].append(prefixo)
        return prefixos_dict
    else:
        st.error(f"Erro ao obter os prefixos: {response.status_code} - {response.text}")
        return {}
    
def enviar_anuncio_bgp(bgp_connector_id, destination_prefix, withdraw_after, comments):
    auth_header = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {auth_header}'
    }
    data = {
        "redirect destination prefix": {
            "bgp_connector_id": bgp_connector_id,
            "destination_prefix": destination_prefix,
            "withdraw_after": withdraw_after,
            "comments": comments
        }
    }
    response = requests.post(f"{API_BASE_URL}/bgp_announcements", headers=headers, json=data)
    if response.status_code == 201:
        anuncio_id = response.json()['href'].split('/')[-1]
        st.success(f"Anúncio BGP enviado com sucesso! ID do anúncio: {anuncio_id}")
    else:
        st.error(f"Erro ao enviar anúncio BGP: {response.status_code} - {response.text}")

def dividir_prefixo_em_24(prefixo):
    rede = ipaddress.IPv4Network(prefixo, strict=False)
    return list(rede.subnets(new_prefix=24))




st.title("Gerenciamento de Prefixos BGP")
tab1, tab2 = st.tabs(["Selecionar prefixos", "Digitar manualmente"])


#-----------------------------SELECIONANDO PREFIXOS-----------------------------#

with tab1:

    prefixos_dict = get_ip_zones()
    if prefixos_dict:
        grupo_selecionado = st.selectbox("Selecione um grupo de prefixos", list(prefixos_dict.keys()))
        prefixos = prefixos_dict.get(grupo_selecionado, [])
        st.write(f"Prefixos no grupo **{grupo_selecionado}**:")
        st.write(prefixos)
        usar_todos = st.checkbox("Usar todos os prefixos")

        if not usar_todos:
            prefixos_selecionados = st.multiselect("Selecione os prefixos desejados", prefixos)
        else:
            prefixos_selecionados = prefixos

        bgp_connectors = requests.get(f"{API_BASE_URL}/bgp_connectors", auth=(USERNAME, PASSWORD)).json()
        bgp_connector_options = {conn['bgp_connector_name']: conn['bgp_connector_id'] for conn in bgp_connectors}
        connector_name = st.selectbox("Selecione o conector BGP", list(bgp_connector_options.keys()))
        connector_id = bgp_connector_options[connector_name]
        withdraw_after = st.number_input("Tempo de anúncio em segundos (0 para infinito)", min_value=0, value=0)
        comments = st.text_input("Comentários para o anúncio")

        if st.button("Enviar anúncio"):
            for prefixo in prefixos_selecionados:
                sub_redes = dividir_prefixo_em_24(prefixo)
                for sub_rede in sub_redes:
                    enviar_anuncio_bgp(connector_id, str(sub_rede), withdraw_after, comments)

with tab2:
    st.subheader("Inserir Prefixos Manualmente")
    
    # Lista para armazenar os prefixos selecionados
    if "prefixos_selecionados" not in st.session_state:
        st.session_state.prefixos_selecionados = []

    # Entrada para adicionar um prefixo
    manual_prefix = st.text_input("Digite o prefixo (exemplo: 189.1.48.0/20):")

    # Botão para adicionar prefixo à lista
    if st.button("Adicionar Prefixo"):
        if manual_prefix:
            try:
                # Validar e dividir o prefixo em sub-redes /24
                sub_redes = dividir_prefixo_em_24(manual_prefix)
                for sub_rede in sub_redes:
                    if str(sub_rede) not in st.session_state.prefixos_selecionados:
                        st.session_state.prefixos_selecionados.append(str(sub_rede))
                st.success(f"Prefixo {manual_prefix} dividido em sub-redes /24 e adicionado com sucesso!")
            except ValueError:
                st.error("Prefixo inválido. Por favor, tente novamente.")
        else:
            st.warning("Digite um prefixo antes de clicar em adicionar.")
    
    # Exibir os prefixos já adicionados
    if st.session_state.prefixos_selecionados:
        st.write("Prefixos adicionados:")
        for prefixo in st.session_state.prefixos_selecionados:
            st.write(f"- {prefixo}")
    
    # Botão para limpar a lista de prefixos
    if st.button("Limpar Lista de Prefixos"):
        st.session_state.prefixos_selecionados = []
        st.info("Lista de prefixos limpa.")
    
    # Seleção de conector BGP (reutilizando lógica de tab1)
    bgp_connectors = requests.get(f"{API_BASE_URL}/bgp_connectors", auth=(USERNAME, PASSWORD)).json()
    bgp_connector_options = {conn['bgp_connector_name']: conn['bgp_connector_id'] for conn in bgp_connectors}
    connector_name = st.selectbox("Selecione o conector BGP", list(bgp_connector_options.keys()), key="manual_connector")
    connector_id = bgp_connector_options[connector_name]
    
    withdraw_after = st.number_input("Tempo de anúncio em segundos (0 para infinito)", min_value=0, value=0, key="manual_withdraw")
    comments = st.text_input("Comentários para o anúncio", key="manual_comments")
    
    # Botão para enviar anúncio
    if st.button("Enviar anúncio", key="manual_enviar"):
        for prefixo in st.session_state.prefixos_selecionados:
            enviar_anuncio_bgp(connector_id, prefixo, withdraw_after, comments)
