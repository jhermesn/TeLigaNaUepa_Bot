# Te Liga na UEPA BOT

Um bot para Discord que monitora o site da UEPA em busca de novos editais e os publica em um canal específico.

## ✨ Funcionalidades

- Monitoramento automático de novos editais no site da UEPA.
- Publicação de novos editais encontrados em um canal configurável do Discord.
- Comandos para administradores e usuários para gerenciar e interagir com o bot.
- Sistema de cargos para inscrição em notificações.

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior
- Git

### 1. Clonar o Repositório

```bash
git clone https://github.com/jhermesn/TeLigaNaUepa_Bot.git
cd TeLigaNaUepa_Bot
```

### 2. Instalar as Dependências

É recomendado criar um ambiente virtual (virtualenv):

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

Instale as dependências a partir do `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configurar as Variáveis de Ambiente

Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`. Este arquivo não será enviado para o repositório e guardará suas variáveis secretas.

```bash
cp .env.example .env
```

Agora, abra o arquivo `.env` e preencha as variáveis, especialmente o `DISCORD_TOKEN`:

```ini
# Token do seu bot no Discord (Obrigatório)
DISCORD_TOKEN="SEU_TOKEN_AQUI"

# Intervalo em minutos para checar por novos editais (Padrão: 5)
CHECK_INTERVAL_MINUTES="5"

# Nível de log (Padrão: INFO)
LOG_LEVEL="INFO"

# Caminho para o arquivo do banco de dados (Padrão: data/uepa_bot.db)
DATABASE_FILE="data/uepa_bot.db"

# URL da página de editais da UEPA
UEPA_EDITAIS_URL="https://www.uepa.br/pt-br/editais"

# Ambiente de execução (development ou production)
ENVIRONMENT="production"

# Timezone
TZ="America/Sao_Paulo"
```

### 4. Executar o Bot

```bash
python main.py
```
## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*. 