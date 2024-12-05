# wanguard_manager
## A graphical interface to manage some functions that are not available on the Wanguard web.


Instale Dependências de Compilação:

    sudo apt update
    sudo apt install build-essential libssl-dev libffi-dev python3-dev

Criar um Ambiente Virtual (Recomendado)

O uso de um ambiente virtual (venv) é a forma mais segura e recomendada para gerenciar dependências do Python sem interferir no sistema.
Passos:

Instalar o python3-venv:

    sudo apt install python3-venv

Crie um ambiente virtual:

    python3 -m venv venv

Ative o ambiente virtual:

Linux/MacOS:

    source venv/bin/activate

Windows:

    venv\Scripts\activate

Instale as dependências no ambiente virtual:

    pip install -r requirements.txt

Execute seu código dentro do ambiente virtual. Quando terminar, você pode desativar o ambiente com:

    deactivate
