# 📰 News Briefing AI — Resumos 3 Vezes por Dia com RSS & Google Gemini

Sistema inteligente para extrair manchetes dos principais veículos de imprensa do Brasil, do Paraná e do mundo, com publicação automática de **resumos 3 vezes por dia (08h, 13h e 19h)**, deduplicação de coberturas e síntese executiva utilizando o **Google Gemini** (`gemini-2.5-flash` via SDK oficial `google-genai`).

---

## ⏰ As 3 Edições Diárias

O sistema gera boletins dinâmicos adaptados ao ciclo de notícias do dia:

| Edição | Horário (BRT) | Janela de Cobertura | Foco Principal |
| :--- | :---: | :---: | :--- |
| 🌅 **Manhã** | **08:00** | Últimas 14 horas | Acontecimentos da noite anterior e primeiras horas do dia |
| ☀️ **Tarde** | **13:00** | Últimas 6 horas | Fatos da manhã, trânsito, decisões do início do dia |
| 🌙 **Noite** | **19:00** | Últimas 7 horas | Desdobramentos da tarde, fechamento de mercados e trânsito de volta para casa |

---

## 🚀 Funcionalidades Principais

- **📡 Coleta Paralela de Múltiplos Portais**:
  - **Fatos da Região (Curitiba & PR)**: Tribuna do Paraná, Bem Paraná, Banda B e Gazeta do Povo.
  - **Briefing Geral (Brasil & Mundo)**: Reuters, CNN, UOL, G1, BBC e InfoMoney.
  - *Customizável:* adicione qualquer feed em `news_briefing/feeds.json` ou `feeds_regional.json`.
- **⏳ Janela Temporal Dinâmica**:
  - Ajusta automaticamente o filtro de horas para não repetir notícias entre as edições da manhã, tarde e noite.
- **🔍 Deduplicação e Agrupamento de Histórias**:
  - Identifica quando múltiplos portais noticiam o mesmo fato e sintetiza em um único item analítico com citação de todas as fontes.
- **🧠 Síntese Editorial com Google Gemini**:
  - Gera resumos executivos estruturados por categorias (Destaques, Segurança, Trânsito, Política, Economia, etc.).
- **🌐 Portal Web Integrado (Vercel)**:
  - As novas edições são automaticamente publicadas e arquivadas no portal estático (`public/`), com leitor modal integrado e filtros por período.
- **📊 Múltiplos Formatos de Saída**:
  - **HTML**: Formatado e responsivo salvo em `reports/` e `public/data/editions/`.
  - **Markdown**: Arquivo `.md` salvo em `reports/`.
  - **Terminal Visual**: Exibição rica no terminal via biblioteca `rich`.
- **📱 Envio via WhatsApp (CallMeBot)**:
  - Envio direto de cada edição para o seu celular.

---

## 📦 Instalação e Configuração

### 1. Pré-requisitos
Python 3.10+ instalado.

### 2. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 3. Configurar `.env`
Crie ou edite o seu arquivo `.env` com a sua chave do [Google AI Studio](https://aistudio.google.com/app/apikey):

```ini
GEMINI_API_KEY=sua_chave_do_google_ai_studio_aqui
GEMINI_MODEL=gemini-2.5-flash
BRIEFING_LANGUAGE=pt-BR

# WhatsApp (Opcional - CallMeBot)
WHATSAPP_ENABLED=false
WHATSAPP_PHONE=5541999999999
WHATSAPP_APIKEY=1234567
```

> **Nota:** Se executado sem chave de IA, o sistema entra automaticamente no **modo estruturado (fallback)**, organizando e gerando o relatório com links das fontes sem quebrar.

---

## 💻 Como Usar

### 1. Fatos da Região (Curitiba & Paraná)
Gera o boletim focado em Curitiba, RMC e Paraná (Tribuna PR, Bem Paraná, Banda B, Gazeta do Povo):
```powershell
python run_fatos_da_regiao.py
```
*(Calcula dinamicamente a janela de horas de acordo com o horário atual).*

Para especificar uma janela manual:
```powershell
python run_fatos_da_regiao.py --hours 12
```

### 2. Briefing Geral (Nacional & Internacional)
Gera o resumo das agências nacionais e mundiais:
```powershell
python run_briefing.py
```

### 3. Modo Dry-Run (Teste sem consumir cota do Gemini)
```powershell
python run_fatos_da_regiao.py --dry-run
python run_briefing.py --dry-run
```

---

## ⏰ Automação dos 3 Horários (08h, 13h e 19h)

### Opção A: GitHub Actions (Nuvem / Vercel — Recomendado)
O repositório já conta com o workflow `.github/workflows/daily_briefing.yml` configurado com cron nos 3 horários:
- `11:00 UTC` = **08:00 BRT**
- `16:00 UTC` = **13:00 BRT**
- `22:00 UTC` = **19:00 BRT**

A cada execução, o GitHub Actions gera as edições, atualiza `public/data/` e faz o push no Git, acionando o deploy automático na Vercel.

### Opção B: Agendador de Tarefas do Windows (schtasks)
Para rodar silenciosamente na sua máquina:

1. Gere os comandos para as 3 tarefas:
   ```powershell
   python run_fatos_da_regiao.py --register-task all
   python run_briefing.py --register-task all
   ```
2. Abra o **Prompt de Comando (CMD)** como Administrador e cole os comandos gerados. Eles criarão as tarefas agendadas para **08:00, 13:00 e 19:00**.

### Opção C: Monitor Contínuo no Terminal
Deixe o terminal aberto aguardando os 3 horários:
```powershell
python run_fatos_da_regiao.py --schedule
```
*(Ou especifique horários customizados: `python run_fatos_da_regiao.py --schedule "08:00,13:00,19:00"`).*

---

## 📱 Envio Gratuito pelo WhatsApp (CallMeBot)

1. Salve o número do CallMeBot na sua agenda: **`+34 644 44 49 64`**.
2. Envie uma mensagem no WhatsApp com o texto:
   `I allow callmebot to send me messages`
3. O bot responderá com sua `apikey`.
4. Insira `WHATSAPP_ENABLED=true`, `WHATSAPP_PHONE` e `WHATSAPP_APIKEY` no seu `.env`.
5. Teste o envio:
   ```powershell
   python run_fatos_da_regiao.py --test-whatsapp
   ```

---

## 📁 Estrutura do Projeto

```
antigravity/
├── .github/workflows/
│   └── daily_briefing.yml     # Cron das 3 edições diárias (08h, 13h, 19h)
├── news_briefing/
│   ├── config.py              # Configurações e variáveis de ambiente
│   ├── feeds.json             # Feeds gerais (Reuters, CNN, UOL, etc.)
│   ├── feeds_regional.json    # Feeds regionais (Tribuna PR, Bem Paraná, Banda B, Gazeta do Povo)
│   ├── fetcher.py             # Coletor RSS multithread com parsing de datas flexível
│   ├── deduplicator.py        # Filtro temporal e agrupamento inteligente de notícias
│   ├── gemini_synthesizer.py  # Síntese editorial com Google Gemini para as 3 edições
│   ├── formatters.py          # Gerador HTML moderno, Markdown e arquivador para Vercel
│   └── scheduler.py           # Agendador das 3 edições e gerador schtasks
├── public/                    # Portal Web publicado na Vercel
│   ├── index.html             # Interface web responsiva com leitor e filtros
│   ├── app.js                 # Lógica de renderização das edições
│   ├── style.css              # Tema escuro executivo
│   └── data/
│       ├── archive_index.json # Índice histórico de edições
│       └── editions/          # Páginas HTML completas das edições
├── reports/                   # Relatórios locais gerados
├── run_fatos_da_regiao.py     # CLI do Fatos da Região (Curitiba & PR)
├── run_briefing.py            # CLI do Briefing Geral
├── requirements.txt           # Dependências Python
└── README_BRIEFING.md         # Documentação do projeto
```
