# 📘 Guia de Instalação e Execução do Aplicativo

Olá! Este é um guia completo para você configurar e rodar o seu novo aplicativo de anotações particulares, ele foi desenvolvimento em Python, utilizando a biblioteca Streamlit e o MongoDB como banco de dados. Além disso, tem MFA.

Siga os passos com atenção e tudo dará certo! 🚀

---

## 📖 Premissas?

1. **MongoDB:** Crie uma conta gratuita https://www.mongodb.com/ e conecte com sua IDE ou utilize instalado localmente, se preferir.  
2. **Escolha sua IDE:** Aqui utilizei o VSCode com a extensão: MongoDB for VS Code.  
3. **Crie sua chave de 32 caracteres:** Gere uma aqui: https://www.devtools24.com/pt/api-key-generator/ e anote.
4. **Insira essa chave no seu app autenticador de preferência:** Ao invés de ler QRCode, use o código e nomeie como "Portal de Anotações"
5. **Seguir orientações abaixo:** Seguir o passo a passo para colocar o sistema para funcionar.

---

## 🧩 Passo 1: Preparar o Ambiente Python e o Projeto

Agora vamos preparar o ambiente para rodar o código do nosso aplicativo.

### 💾 Instale o Python 3.13 ou Superior

1. Acesse [python.org](https://www.python.org/downloads/) e baixe a versão **3.13**.  
2. Durante a instalação, **marque a caixa** `Add Python to PATH` antes de clicar em **Install Now**.

### 🧭 Abra o Terminal de sua preferência e Obtenha os Arquivos do Projeto

```bash
cd PastadoProjeto
git clone https://github.com/emersonaparecidosilva/anotacoes-pessoais

### Habilite o ambiente Virtual
python -m venv .venv

### Ative o ambiente
.venv\Scripts\activate

### Caso os scripts estejam bloqueados:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

### Instale as bibliotecas 
pip install -r requirements.txt
````

### 🧩 Passo 2: Configurar o Arquivo de Segredos (secrets.toml)
- Crie a Pasta .streamlit
    - Dentro da pasta do projeto, crie uma nova pasta e renomeie-a para exatamente .streamlit (com o ponto no início).

-  Crie e edite o arquivo secrets.toml, cole o conteúdo abaixo e salve o arquivo dentro da pasta .streamlit.
  
```bash
# Coloque aqui as credenciais do seu banco de dados local/remoto MySQL
[mongodb]
# Substitua pela sua string de conexão copiada do MongoDB Atlas
uri = "mongodb+srv://user:senha@instanciamongodb.com"
db_name = "portal_anotacoes"

[auth]
# Defina a senha que você usará para entrar no portal
senha_painel = "SuaSenha"

# Chave secreta de 32 caracteres (A-Z, 2-7) para o algoritmo do 2FA. 
# Exemplo de chave válida (altere alguns caracteres para a sua segurança):
chave_2fa_master = "Chave criada na premissa de número 3"
````
    
### 🧩 Passo 3: Rode o app pelo terminal na pasta do projeto

```bash
streamlit run app.py
````

- Observe o retorno no terminal:
  
```bash
2026-05-23 09:43:56.748 Uvicorn server started on 0.0.0.0:8501

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.102:8501


````  

### 🧩 Passo 4: Abra o sistema, coloque a senha o código gerado no seu app autenticador

### 🧩 Passo 5: Utilizar o sistema, gerar suas notas conforme necessidade. Elas estaram sempre disponíveis na aba "Buscar e Editar".

### 💾 Dica Extra: Publique seu APP na Streamlit Cloud Community e tenha suas anotações disponíveis 24x7.
