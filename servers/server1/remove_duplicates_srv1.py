import streamlit as st
import requests
import yaml
from collections import defaultdict

def carregar_configuracoes(caminho_arquivo):
    with open(caminho_arquivo, 'r') as file:
        configuracoes = yaml.safe_load(file)
    return configuracoes

config = carregar_configuracoes(r"../config/config.yaml")

servidor = config['Server1']
USERNAME = servidor['username']
PASSWORD = servidor['password']
API_BASE_URL = servidor['api_base_url']

st.title(f"{servidor['name']} - Remover Duplicados ")

anuncio_opcao = st.radio("Qual anúncio manter?", ["Primeiro", "Último"])

def obter_anuncios_ativos():
    url = f'{API_BASE_URL}/bgp_announcements?status=Active&fields=bgp_announcement_id%2Cstatus%2Cprefix'
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao obter anúncios: {response.status_code} - {response.text}")
        return []

def retirar_anuncio(bgp_announcement_id):
    url = f'{API_BASE_URL}/bgp_announcements/{bgp_announcement_id}/status?status=Finished'
    response = requests.put(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        st.success(f"Anúncio {bgp_announcement_id} retirado com sucesso.")
    else:
        st.error(f"Erro ao retirar anúncio {bgp_announcement_id}: {response.status_code} - {response.text}")

def remover_duplicatas(anuncios):
    prefixos_dict = defaultdict(list)
    for anuncio in anuncios:
        prefixo = anuncio['prefix']
        prefixos_dict[prefixo].append(anuncio)
    for prefixo, lista_anuncios in prefixos_dict.items():
        if len(lista_anuncios) > 1:
            st.write(f"Anúncios duplicados encontrados para o prefixo {prefixo}:")
            if anuncio_opcao == "Primeiro":
                for anuncio in lista_anuncios[1:]:
                    retirar_anuncio(anuncio['bgp_announcement_id'])
            elif anuncio_opcao == "Último":
                for anuncio in lista_anuncios[:-1]:
                    retirar_anuncio(anuncio['bgp_announcement_id'])

anuncios_ativos = obter_anuncios_ativos()

if st.button("Remover duplicados"):
    if anuncios_ativos:
        remover_duplicatas(anuncios_ativos)
    else:
        st.warning("Nenhum anúncio ativo encontrado.")
