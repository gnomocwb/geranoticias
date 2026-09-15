# 📰 Gera Notícias (Gnomo CWB) — News Briefing AI com Google Gemini

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-4285F4.svg?style=flat&logo=google&logoColor=white)](https://aistudio.google.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg?style=flat&logo=githubactions&logoColor=white)](https://github.com/gnomocwb/geranoticias/actions)
[![Vercel Deployment](https://img.shields.io/badge/Deploy-Vercel-000000.svg?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema inteligente e autônomo para coleta, deduplicação editorial e síntese de notícias dos principais portais de imprensa do **Paraná**, do **Brasil**, do **Mundo** e da **comunidade autista (TEA)**. O sistema gera resumos analíticos com o **Google Gemini** (`gemini-2.5-flash` via SDK oficial `google-genai`), publica automaticamente em um portal web moderno hospedado na **Vercel** e envia resumos diários para o **WhatsApp**.

---

## 🕒 Ciclo de Edições Diárias

O sistema opera com horários programados de acordo com o fluxo de notícias:

| Edição | Horário (BRT) | Módulo | Janela de Cobertura | Foco Principal |
| :--- | :---: | :--- | :---: | :--- |
| 🌅 **Manhã** | **08:00** | Fatos da Região + Brasil | Últimas 14 horas | Acontecimentos da noite anterior e primeiras notícias do dia |
| 🧩 **Autismo** | **09:00** | Notícias Autismo Brasil | Últimas 24 horas | Decisões jurídicas, direitos, saúde, pesquisas e inclusão TEA |
| ☀️ **Tarde** | **13:00** | Fatos da Região + Brasil | Últimas 6 horas | Fatos da manhã, trânsito, decisões administrativas e do judiciário |
| 🌙 **Noite** | **19:00** | Fatos da Região + Brasil | Últimas 7 horas | Desdobramentos da tarde, economia, fechamento de mercados e volta para casa |

---

## 🚀 Os 3 Módulos de Notícias

### 1. 🏙️ Fatos da Região (Curitiba, RMC & Interior do Paraná)
Cobertura hiperlocal focada na capital paranaense, região metropolitana e polos do interior:
- **Curitiba & Região Metropolitana**: *Tribuna do Paraná*, *Bem Paraná*, *Banda B*, *Gazeta do Povo*.
- **Interior do Estado**:
  - *O Maringá* (Noroeste)
  - *Folha de Londrina* (Norte)
  - *Diário de Foz* (Oeste & Tríplice Fronteira)
  - *Rede Sul de Notícias* (Guarapuava & Centro-Sul)
- **Execução**: `python run_fatos_da_regiao.py`

### 2. 🇧🇷 Notícias Brasil & Mundo
Síntese dos fatos de maior relevância política, econômica e internacional:
- **Veículos Monitorados**: *G1*, *UOL Notícias*, *CNN Brasil*, *BBC News Brasil*, *Reuters*, *InfoMoney*.
- **Execução**: `python run_briefing.py`

### 3. 🧩 Notícias Autismo Brasil (Gera Notícias Autistas)
Monitoramento especializado diário sobre o Transtorno do Espectro Autista:
- **Temas**: Direitos e legislação, decisões judiciais de planos de saúde/SUS, terapias baseadas em evidências, inclusão escolar e social, pesquisas científicas e eventos.
- **Veículos Monitorados**: *Canal Autismo (Revista Autismo)*, *Agência Brasil*, seções especializadas de direitos e saúde.
- **Execução**: `python run_noticias_autismo.py`

---

## ✨ Funcionalidades Principais

- **📡 Coleta Paralela em Tempo Real**: Extração multithread de feeds RSS com suporte flexível a múltiplos padrões de data (RFC 822, ISO 8601 e variações em português).
- **⏳ Janela Temporal Dinâmica**: Ajuste automático da faixa de horas conforme a edição atual, garantindo que notícias já vistas não sejam repetidas.
- **🔍 Agrupamento e Deduplicação Inteligente**: Algoritmo que detecta quando múltiplos portais cobrem o mesmo fato, unificando em um único tópico com menção e citação de todas as fontes.
- **🧠 Síntese Editorial com Google Gemini**: Geração de resumos executivos estruturados por categorias, com tom jornalístico sério, imparcial e links originais para leitura completa.
- **🛡️ Fallback Estruturado sem Quebra**: Caso a chave da API não esteja presente ou a cota temporária termine, o sistema opera em modo de contingência estruturado, organizando o boletim normalmente sem falhar.
- **🌐 Portal Web Integrado (Vercel)**:
  - Layout dark mode responsivo moderno (Plus Jakarta Sans & JetBrains Mono).
  - Filtros rápidos por edição (Todas, 🌅 Manhã, ☀️ Tarde, 🌙 Noite).
  - Botões de acesso rápido: **Acessar Report Brasil** e **Acessar Report Autismo**.
  - Busca instantânea por palavras-chave, cidades ou temas.
  - Leitor modal em tela cheia com visual limpo e sem distrações.
  - Métricas com **Vercel Web Analytics**.
- **📱 Notificações via WhatsApp**: Envio automatizado do boletim para seu número utilizando a API do **CallMeBot**.
- **📊 Múltiplos Formatos de Saída**: Salva relatórios em HTML moderno responsivo, Markdown (`reports/`), JSON para o portal e exibição formatada no terminal via biblioteca `rich`.

---

## 📦 Instalação e Configuração

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git

### 2. Clonar o Repositório e Instalar Dependências
```bash
git clone https://github.com/gnomocwb/geranoticias.git
cd geranoticias
python -m venv .venv
```

No Windows (PowerShell):
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux / macOS:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente (`.env`)
Copie o arquivo de exemplo ou crie o seu `.env`:
```ini
# Chave da API do Google AI Studio (Gratuita)
# Obtenha em: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=sua_chave_do_google_ai_studio_aqui
GEMINI_MODEL=gemini-2.5-flash
BRIEFING_LANGUAGE=pt-BR

# Envio via WhatsApp (Opcional - CallMeBot)
WHATSAPP_ENABLED=false
WHATSAPP_PHONE=5541999999999
WHATSAPP_APIKEY=sua_apikey_callmebot

# Diretório customizado para relatórios de autismo (Opcional)
# Exemplo: C:\Users\usuario\OneDrive\Documentos\Autismo
AUTISMO_REPORTS_DIR=
```

---

## 💻 Como Usar (Linha de Comando)

### Fatos da Região (Curitiba & PR)
```bash
# Execução padrão (calcula automaticamente a janela temporal da edição)
python run_fatos_da_regiao.py

# Especificar janela manual de horas
python run_fatos_da_regiao.py --hours 12

# Teste sem consumir cota do Gemini (Dry-Run)
python run_fatos_da_regiao.py --dry-run
```

### Notícias Brasil & Mundo
```bash
python run_briefing.py
python run_briefing.py --dry-run
```

### Notícias Autismo Brasil
```bash
python run_noticias_autismo.py
python run_noticias_autismo.py --hours 24
```

### Agendador Local e Notificações
```bash
# Deixar em monitoramento contínuo no terminal
python run_fatos_da_regiao.py --schedule

# Testar envio para o WhatsApp
python run_fatos_da_regiao.py --test-whatsapp

# Gerar comandos do Agendador de Tarefas do Windows (schtasks)
python run_fatos_da_regiao.py --register-task all
```

---

## ☁️ Automação com GitHub Actions

O repositório inclui fluxos de trabalho prontos em `.github/workflows/`:

1. **`daily_briefing.yml`**:
   - Executa 3 vezes ao dia: às **08:00**, **13:00** e **19:00** (Horário de Brasília).
   - Roda `run_fatos_da_regiao.py` e `run_briefing.py`.
   - Salva e comita as edições em `public/data/` e `reports/`.
   - Aciona automaticamente o deploy da nova versão na Vercel.

2. **`daily_briefing_autismo.yml`**:
   - Executa 1 vez ao dia: às **09:00** (Horário de Brasília).
   - Roda `run_noticias_autismo.py`.
   - Salva e comita o boletim diário de autismo.

### Secrets do Repositório (GitHub Actions)
Para ativar a execução em nuvem, acesse **Settings > Secrets and variables > Actions** no seu repositório do GitHub e adicione:
- `GEMINI_API_KEY`: sua chave de API do Google Gemini.
- `WHATSAPP_ENABLED`: `true` ou `false`.
- `WHATSAPP_PHONE`: número com DDI e DDD (ex.: `5541999999999`).
- `WHATSAPP_APIKEY`: sua chave de API do CallMeBot.

---

## 📱 Notificações no WhatsApp com CallMeBot (Gratuito)

1. Adicione o contato do CallMeBot no WhatsApp: **`+34 644 44 49 64`**.
2. Envie a mensagem de ativação:
   ```text
   I allow callmebot to send me messages
   ```
3. O bot responderá com sua `apikey`.
4. Preencha as variáveis correspondentes no arquivo `.env` ou nas Secrets do GitHub.

---

## 📁 Estrutura do Repositório

```
geranoticias/
├── .github/workflows/
│   ├── daily_briefing.yml          # Automação 3x ao dia (08h, 13h, 19h)
│   └── daily_briefing_autismo.yml  # Automação diária de Autismo (09h)
├── news_briefing/
│   ├── config.py                   # Gerenciamento de variáveis e caminhos
│   ├── deduplicator.py             # Filtro por janela temporal e agrupamento
│   ├── feeds.json                  # Feeds de Notícias Brasil e Mundo
│   ├── feeds_regional.json         # Feeds de Curitiba e Interior do Paraná
│   ├── feeds_autismo.json          # Feeds especializados em Autismo (TEA)
│   ├── fetcher.py                  # Extrator RSS multithread resiliente
│   ├── formatters.py               # Gerador de HTML, Markdown e arquivador JSON
│   ├── gemini_synthesizer.py       # Integração com Google Gemini (prompts e fallback)
│   ├── scheduler.py                # Agendador interno e gerador de rotinas schtasks
│   └── whatsapp_sender.py          # Envio automatizado de mensagens via CallMeBot
├── public/                         # Portal Web publicado na Vercel
│   ├── index.html                  # Interface gráfica responsiva com filtros e busca
│   ├── style.css                   # Estilização moderna Dark Mode
│   ├── app.js                      # Lógica interativa, renderização de cards e leitor modal
│   └── data/
│       ├── archive_index.json      # Índice estruturado com histórico de todas as edições
│       └── editions/               # Relatórios HTML completos arquivados
├── reports/                        # Relatórios locais gerados (HTML e Markdown)
├── tests/
│   ├── test_briefing.py            # Testes unitários do pipeline principal
│   └── test_autismo_briefing.py    # Testes unitários do módulo de autismo
├── run_fatos_da_regiao.py          # CLI do Fatos da Região (Curitiba & PR)
├── run_briefing.py                 # CLI do Notícias Brasil & Mundo
├── run_noticias_autismo.py         # CLI do Notícias Autismo Brasil
├── requirements.txt                # Dependências Python do projeto
├── vercel.json                     # Configuração de cache e roteamento da Vercel
└── README.md                       # Documentação oficial do projeto
```

---

## 🧪 Testes Automatizados

Para executar os testes unitários do projeto:

```powershell
python -m unittest discover tests
```

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.
