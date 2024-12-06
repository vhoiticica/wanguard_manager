import streamlit as st

def carregar_configuracoes(caminho_arquivo):
    with open(caminho_arquivo, 'r') as file:
        configuracoes = file.read()  
    return configuracoes

config = carregar_configuracoes(r"../config/config.yaml")

st.title('Arquivo de configuração')
st.code(config, language='yaml')
