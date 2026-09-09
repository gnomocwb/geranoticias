# Chrome RAM Saver & Auto Tab Discarder (Manifest V3)

Extensão de alto desempenho para Google Chrome criada para **liberar memória RAM continuamente**, **suspender abas inativas há mais de 20 minutos**, **limpar cache de rede sob demanda e programado**, e acelerar a navegação.

---

## 🚀 Como Funciona

### 1. Suspensão Nativa de Abas (`chrome.tabs.discard`)
Ao contrário de soluções que fecham suas abas ou usam páginas intermediárias lentas, esta extensão utiliza a API oficial do Chromium de **descarte de processos**.
- **O que acontece?** A aba permanece na sua barra superior (com título e favicon normais), mas o processo de renderização associado é 100% desalocado da memória RAM.
- **Como restaurar?** Basta clicar na aba novamente: o Chrome a recarrega instantaneamente do ponto em que você parou.
- **Economia típica:** entre **80 MB e 250 MB por aba** suspensa.

### 2. Monitoramento Inteligente de Inatividade (Padrão: 20 min)
- Um alarme em segundo plano (`chrome.alarms`) monitora a última vez que cada aba esteve em foco.
- Se atingir o tempo limite configurado (5m, 10m, 15m, 20m, 30m ou 1h), a aba é automaticamente descartada.
- **Proteções ativas:**
  - Nunca suspende a aba que você está usando no momento.
  - Não suspende abas reproduzindo áudio/vídeo (YouTube, Spotify, Google Meet, Teams, Discord).
  - Não suspende abas fixadas (pinned).
  - Respeita sua lista de permissões (**Whitelist**).

### 3. Limpeza de Cache de Rede (`chrome.browsingData`)
- Limpa o cache HTTP em disco e em memória e o cache de service workers.
- **100% Seguro:** Não desloga de contas, não apaga senhas, não apaga favoritos nem histórico de navegação.
- Pode ser acionado com 1 clique no painel ou configurado para limpeza automática a cada 24 horas.

### 4. Fechador Inteligente de Abas Duplicadas
- **Detecção Avançada:** Varre todas as janelas abertas e normaliza as URLs (remove âncoras/hashes `#`, padroniza barras finais e ordena parâmetros de busca para identificar duplicatas mesmo com variações sutis).
- **Prioridade Inteligente:** Ao detectar abas idênticas, a extensão preserva inteligentemente a aba ativa na sua janela atual, abas tocando áudio ou abas fixadas, fechando apenas as cópias ociosas em segundo plano.
- **Contador em Tempo Real:** O botão no popup exibe a quantidade exata de repetidas detectadas no momento (`Fechar Repetidas (N)`).
- **Modo Automático:** Nas configurações da extensão, você pode ativar o switch **"Fechar duplicadas automaticamente"** para que o Chrome descarte abas repetidas assim que forem abertas.

---

## 📦 Como Instalar no Google Chrome (Passo a Passo)

1. Abra o **Google Chrome**.
2. Digite na barra de endereços:
   ```text
   chrome://extensions
   ```
   e pressione `Enter`.
3. No canto superior direito, ative a chave **"Modo do desenvolvedor"** (Developer mode).
4. No canto superior esquerdo, clique no botão **"Carregar sem compactação"** (Load unpacked).
5. Selecione a pasta deste projeto:
   ```text
   c:\Users\mlori\toco\antigravity
   ```
6. Pronto! O ícone com o raio azul/ciano aparecerá na barra de ferramentas do seu Chrome.
   *(Dica: clique no ícone de "quebra-cabeça" na barra do Chrome e clique no alfinete para fixar o ícone da extensão).*

---

## ⚡ Mais Dicas de Performance Nativa para o Chrome

Além de usar a extensão, execute estes ajustes para extrair a máxima velocidade do Chrome:

### 1. Ajustar o Economizador de Memória Nativo
- Acesse `chrome://settings/performance`
- Certifique-se de que o **Economizador de memória (Memory Saver)** está ativado.
- Se disponível na sua versão do Chrome, selecione o modo **Máximo** ou **Agressivo**.

### 2. Desativar Aplicativos em Segundo Plano ao Fechar o Chrome
- Acesse `chrome://settings/system`
- Desmarque a opção: **"Continuar executando aplicativos em segundo plano quando o Google Chrome estiver fechado"**. Isso evita que processos órfãos fiquem comendo RAM mesmo após fechar o navegador.

### 3. Monitorar o Consumo com o Gerenciador de Tarefas do Chrome
- Pressione `Shift + Esc` em qualquer tela do Chrome.
- Você verá exatamente quanta memória cada aba, extensão e processo GPU está consumindo em tempo real.
- Ao clicar em **"Liberar Memória Agora"** no popup da extensão, você verá os processos das abas inativas desaparecerem instantaneamente do gerenciador de tarefas!

---

## 🛠️ Estrutura dos Arquivos

- `manifest.json` — Manifesto Manifest V3 com permissões mínimas essenciais.
- `background/service-worker.js` — Motor em segundo plano para rastreamento de atividade, descarte periódico e limpeza de cache.
- `popup/popup.html` — Interface gráfica moderna (Dark Mode, Glassmorphism).
- `popup/popup.css` — Estilos visuais, micro-animações e temas.
- `popup/popup.js` — Lógica reativa do painel, métricas e atalhos.
- `icons/` — Ícones PNG nítidos (16x16, 48x48, 128x128).
- `scripts/generate_icons.py` — Script gerador de ícones independente.
