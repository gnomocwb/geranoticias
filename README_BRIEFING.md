# 🌅 News Briefing AI — Briefing Matinal com RSS & Google Gemini

Sistema inteligente para extrair manchetes dos principais veículos de imprensa do Brasil e do mundo (**Reuters, CNN, UOL, G1, BBC, InfoMoney e outros**) pela manhã, filtrar as notícias recentes da madrugada/início do dia, deduplicar coberturas e gerar um **briefing executivo, único e sucinto** utilizando o **Google Gemini** (`gemini-2.5-flash` via SDK oficial `google-genai`).

---

## 🚀 Funcionalidades Principais

- **📡 Coleta Paralela de Múltiplos Feeds RSS**:
  - **Reuters** (Cobertura global e economia internacional)
  - **CNN** (CNN International e CNN Brasil)
  - **UOL** (UOL Notícias e UOL Economia)
  - **G1 Globo** (Brasil e atualidades)
  - **BBC News** (BBC Brasil e BBC World)
  - **InfoMoney** (Mercados financeiros, ações e negócios)
  - *Customizável:* adicione qualquer RSS no arquivo `news_briefing/feeds.json`.
- **⏳ Filtro Temporal Matinal**:
  - Janela retroativa inteligente (padrão de 16 horas para capturar notícias da madrugada e início da manhã).
  - Parser resiliente que aceita padrões RFC-822, ISO e datas brasileiras em português do UOL (`Qua, 09 Set 2026...`).
- **🔍 Deduplicação e Agrupamento de Histórias**:
  - Agrupa reportagens de diferentes veículos sobre o mesmo fato (ex: Reuters + CNN cobrindo o mesmo acontecimento).
- **🧠 Síntese Editorial com Google Gemini**:
  - Gera um resumo executivo de 3 minutos estruturado por categorias:
    - ⚡ *Destaques da Manhã (Top 3 Acontecimentos)*
    - 🇧🇷 *Brasil & Política*
    - 📈 *Economia, Mercados & Negócios*
    - 🌍 *Cenário Internacional & Geopolítica*
    - 💡 *Tecnologia & Inovação*
    - 🎯 *Radar Rápido (Pílulas em 1 linha)*
    - 🔗 *Citações com links das fontes originais*
- **📊 Múltiplos Formatos de Saída**:
  - **Markdown**: Salvo automaticamente em `reports/briefing_YYYY-MM-DD.md`.
  - **HTML Newsletter**: Salvo em `reports/briefing_YYYY-MM-DD.html` com design moderno, responsivo e elegante.
  - **Terminal Visual**: Renderização colorida com tabelas e painéis via biblioteca `rich`.
- **⏰ Automação Matinal**:
  - Modo `--schedule 07:00` para execução contínua.
  - Gerador de tarefa do **Agendador de Tarefas do Windows (`schtasks`)** para rodar sem precisar de janela aberta.

---

## 📦 Instalação e Configuração

### 1. Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado.

### 2. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 3. Configurar Chave da API do Gemini
Copie o arquivo de exemplo e insira sua chave gratuita obtida no [Google AI Studio](https://aistudio.google.com/app/apikey):

```powershell
copy .env.example .env
```

Edite o arquivo `.env`:
```ini
GEMINI_API_KEY=sua_chave_do_google_ai_studio_aqui
GEMINI_MODEL=gemini-2.5-flash
BRIEFING_HOURS=16
BRIEFING_LANGUAGE=pt-BR
```

> **Nota:** Caso você rode sem a chave, o sistema entra automaticamente em **modo estruturado (fallback)**, organizando e gerando o relatório completo com links sem falhar!

---

## 💻 Como Usar

### 1. Execução Matinal Padrão
Gera o relatório com todas as fontes nas últimas 16 horas e salva em Markdown, HTML e Terminal:
```powershell
python run_briefing.py --morning
```

### 2. Modo Dry-Run (Teste sem gastar cota de IA)
```powershell
python run_briefing.py --morning --dry-run
```

### 3. Filtrar Fontes Específicas
Execute apenas para determinados veículos (ex: apenas Reuters e UOL):
```powershell
python run_briefing.py --feeds reuters,uol_noticias --morning
```

### 4. Ajustar Janela de Horas
Para capturar as notícias das últimas 24 horas:
```powershell
python run_briefing.py --hours 24
```

### 5. Escolher o Formato de Saída
- Somente Terminal: `python run_briefing.py --output cli`
- Somente HTML: `python run_briefing.py --output html`
- Somente Markdown: `python run_briefing.py --output md`
- Todos (padrão): `python run_briefing.py --output all`

---

## 📱 Envio Gratuito pelo WhatsApp (CallMeBot)

Você pode receber o resumo matinal formatado diretamente no seu WhatsApp pessoal de forma 100% gratuita utilizando a API do **CallMeBot**.

### Como Configurar em 2 Minutos:
1. Salve o número do bot do CallMeBot na sua agenda: **`+34 644 44 49 64`** (ou verifique o número ativo em [callmebot.com](https://www.callmebot.com/blog/free-api-whatsapp-messages/)).
2. Abra o WhatsApp e envie a seguinte mensagem para ele:
   ```
   I allow callmebot to send me messages
   ```
3. O bot responderá em instantes com sua chave:
   ```
   API Activated. Your apikey is: 1234567
   ```
4. Adicione no seu arquivo `.env`:
   ```ini
   WHATSAPP_ENABLED=true
   WHATSAPP_PHONE=5541999999999
   WHATSAPP_APIKEY=1234567
   ```
   *(Substitua `5541999999999` pelo seu DDI 55 + DDD + seu número, somente dígitos)*.

5. **Testar o envio:**
   ```powershell
   python run_briefing.py --test-whatsapp
   ```

6. **Enviar o briefing da manhã:**
   ```powershell
   python run_briefing.py --morning --whatsapp
   ```
   *(Se `WHATSAPP_ENABLED=true` estiver no `.env`, o envio é automático sempre que rodar `--morning`)*.


---

## ⏰ Automação Matinal (Executar todos os dias)

### Opção A: Agendador de Tarefas Nativo do Windows (Recomendado)
Para rodar silenciosamente em segundo plano todos os dias às **07:00 da manhã**:

1. Obtenha o comando gerado:
   ```powershell
   python run_briefing.py --register-task "07:00"
   ```
2. Abra o **Prompt de Comando (CMD)** como Administrador e execute o comando exibido:
   ```cmd
   schtasks /create /tn "BriefingMatinalNews" /tr "\"C:\Caminho\Para\python.exe\" \"C:\Users\mlori\toco\antigravity\run_briefing.py\" --morning --output all" /sc daily /st 07:00 /f
   ```

### Opção B: Monitor Contínuo no Terminal
Deixe o script aberto monitorando e disparando às 07:00:
```powershell
python run_briefing.py --schedule "07:00"
```

---

## 🏙️ Fatos da Região — Curitiba & Paraná (Execução às 09:00)

Além do briefing nacional e global, o sistema conta com o informativo **Fatos da Região**, dedicado a cobrir os acontecimentos de **Curitiba, Região Metropolitana (RMC) e Paraná**.

### 📡 Fontes Monitoradas:
- **Tribuna do Paraná** (`https://www.tribunapr.com.br/noticias/`)
- **Bem Paraná** (`https://www.bemparana.com.br/ultimas/`)
- **Banda B** (`https://www.bandab.com.br/ultimas-noticias/`)

Configurados em [`news_briefing/feeds_regional.json`](news_briefing/feeds_regional.json) com suporte a canais diretos e arquivo ampliado das últimas 24 horas.

### 🎯 Seções do Boletim Regional:
- ⚡ **Destaques da Região (Top 3)**
- 🚨 **Segurança Pública & Ocorrências** (acidentes na BR/rápida, ações policiais, Defesa Civil)
- 🚗 **Trânsito, Mobilidade & Cidade** (bloqueios, ônibus, clima, obras)
- ⚖️ **Política Paranaense & Gestão** (Prefeitura de Curitiba, Palácio Iguaçu, Alep)
- 💼 **Economia Local & Negócios** (empresas locais, vagas, comércio e agro paranaense)
- 🎭 **Cidade, Comunidade & Lazer** (parques, cultura, gastronomia)
- 🎯 **Giro RMC & Interior** (São José dos Pinhais, Colombo, Araucária, Fazenda Rio Grande, Litoral e Interior)

### 💻 Como Executar o Fatos da Região:

1. **Execução Imediata (Dia anterior + início da manhã — 22 horas):**
   ```powershell
   python run_fatos_da_regiao.py
   ```

2. **Agendamento Diário às 09:00 no Windows (Recomendado):**
   Gere o comando do Agendador de Tarefas do Windows:
   ```powershell
   python run_fatos_da_regiao.py --register-task 09:00
   ```
   Execute o comando `schtasks` retornado no Prompt de Comando (CMD) como Administrador.

3. **Monitor Contínuo no Terminal:**
   ```powershell
   python run_fatos_da_regiao.py --schedule 09:00
   ```

4. **Enviar para o WhatsApp:**
   ```powershell
   python run_fatos_da_regiao.py --whatsapp
   ```

5. **Modo Dry-Run (Teste sem IA):**
   ```powershell
   python run_fatos_da_regiao.py --dry-run
   ```

---

## ⚙️ Como Adicionar Novos Feeds RSS

Abra o arquivo [`news_briefing/feeds.json`](news_briefing/feeds.json) e adicione seu novo feed:

```json
{
  "id": "meu_feed",
  "name": "Nome do Portal",
  "url": "https://exemplo.com/rss.xml",
  "category": "Economia",
  "language": "pt",
  "enabled": true,
  "description": "Descrição curta do veículo"
}
```

---

## 📁 Estrutura de Pastas

```
antigravity/
├── news_briefing/
│   ├── __init__.py
│   ├── config.py              # Configurações e variáveis de ambiente
│   ├── feeds.json             # Catálogo de feeds RSS configurados
│   ├── fetcher.py             # Coletor multithread com parsing de datas flexível
│   ├── deduplicator.py        # Filtro temporal e agrupamento inteligente de notícias
│   ├── gemini_synthesizer.py  # Integração com google-genai (Gemini 2.5 Flash)
│   ├── formatters.py          # Geradores de Markdown, HTML moderno e Terminal Rich
│   └── scheduler.py           # Agendador matinal e integração com Windows schtasks
├── reports/                   # Relatórios gerados (.md e .html)
├── tests/
│   └── test_briefing.py       # Testes unitários automatizados
├── run_briefing.py            # CLI principal
├── requirements.txt           # Dependências do projeto
├── .env.example               # Template de configuração
└── README_BRIEFING.md         # Este guia
```
