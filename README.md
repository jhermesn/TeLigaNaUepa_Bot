# Te Liga na UEPA BOT

Um bot para Discord que monitora o site da UEPA em busca de novos editais e os publica em um canal específico.

## ✨ Funcionalidades

- Monitoramento automático de novos editais no site da UEPA.
- Publicação de novos editais encontrados em um canal configurável do Discord.
- Comandos para administradores e usuários para gerenciar e interagir com o bot.
- Sistema de cargos para inscrição em notificações.

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.10 ou superior
- Git

### 1. Clonar o Repositório

```bash
git clone https://github.com/jhermesn/TeLigaNaUepa_Bot.git
cd TeLigaNaUepa_Bot
```

### 2. Instalar as Dependências

É recomendado criar um ambiente virtual (virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

Instale as dependências a partir do `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configurar as Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do projeto. Este arquivo não será enviado para o repositório e guardará suas variáveis secretas. Você pode usar o arquivo `.env.example` como base.

```ini
# Discord
DISCORD_TOKEN="your_discord_bot_token"
DISCORD_TEST_GUILD_ID="your_test_server_id" # Opcional: para testes rápidos de comandos

# Banco de Dados
DATABASE_URL="sqlite:///data/uepa_bot.db"

# URLs
UEPA_EDITAIS_URL="https://www.uepa.br/pt-br/editais"

# Logging (opcional)
LOG_LEVEL="INFO" # Pode ser DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 4. Executar o Bot

```bash
python main.py
```

## 🏗️ Estrutura do Projeto

O projeto segue uma arquitetura limpa, separando as responsabilidades em três camadas principais:

- `src/core`: Contém as entidades e regras de negócio da aplicação.
- `src/infra`: Implementações de baixo nível, como acesso a banco de dados, web scraping e logging.
- `src/presentation`: A camada de apresentação, que neste caso é a interface com o Discord (bot e cogs).

A injeção de dependências é gerenciada pela biblioteca `dependency-injector`, com as configurações definidas em `src/containers.py`.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*. 

# 📄 Licença
Este projeto está licenciado sob a [Licença MIT](LICENSE).