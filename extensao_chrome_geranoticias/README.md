# 📰 Extensão Chrome — Gera Notícias (Curitiba, RMC & Autismo) 🧩🏙️

> **Extensão oficial Manifest V3 para Google Chrome com foco exclusivo em Notícias de Curitiba & Região Metropolitana (Fatos da Região) e Notícias sobre Autismo Brasil (TEA).**

---

## ✨ Recursos da Extensão:

1. **Foco Editorial Segmentado**:
   - 🏙️ **Curitiba & RMC**: Edições de 3x ao dia (08h, 13h, 19h) sintetizando notícias locais de Curitiba, trânsito, alertas da Defesa Civil e Paraná (*Tribuna, Bem Paraná, Banda B, Gazeta do Povo*).
   - 🧩 **Autismo Brasil**: Edições diárias especializadas em direitos, saúde, inclusão escolar, avanços científicos e comunidade TEA (*Canal Autismo, Revista Autismo, Agência Brasil*).

2. **Leitor Integrado (Reading Mode)**:
   - Abra a edição completa diretamente no modal da extensão, com links jornalísticos preservados e formatação limpa.

3. **Notificação de Novas Edições**:
   - Um background service worker monitora em segundo plano a cada 30 minutos.
   - Quando sai uma nova edição, o ícone da extensão ganha um selo **NOVO**.

4. **Desempenho Instantâneo (0ms)**:
   - Utiliza `chrome.storage.local` para carregar as últimas notícias em milissegundos mesmo sem conexão ativa, atualizando silenciosamente em segundo plano via GitHub Raw.

---

## 🚀 Como Instalar no Google Chrome (1 Minuto):

1. Abra o seu navegador **Google Chrome**.
2. Digite na barra de endereços:
   ```
   chrome://extensions
   ```
   *(ou vá no menu dos três pontinhos ➔ Extensões ➔ Gerenciar extensões)*.
3. No canto superior direito, ative a chave **"Modo do desenvolvedor"** (*Developer mode*).
4. No canto superior esquerdo, clique no botão **"Carregar sem compactação"** (*Load unpacked*).
5. Selecione a pasta deste projeto:
   ```
   c:\Users\mlori\toco\antigravity\extensao_chrome_geranoticias
   ```
6. Pronto! A extensão aparecerá instalada.
7. Clique no ícone de "quebra-cabeça" na barra de ferramentas do Chrome e **fixe (pin)** o ícone do **Gera Notícias** para acesso rápido com 1 clique!

---

## 📂 Estrutura de Arquivos:

```
extensao_chrome_geranoticias/
├── manifest.json              # Configuração Manifest V3
├── icons/                     # Ícones gerados em 16x16, 48x48 e 128x128
│   ├── icon-16.png
│   ├── icon-48.png
│   └── icon-128.png
├── popup/
│   ├── popup.html             # Interface com abas Curitiba & Autismo
│   ├── popup.css              # Dark mode elegante e micro-animações
│   └── popup.js               # Consumo de dados e renderizador do leitor
├── background/
│   └── service-worker.js      # Verificação periódica de novas edições
└── README.md
```
