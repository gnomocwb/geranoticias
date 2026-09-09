# Chrome Web Store Listing — Chrome RAM Saver & Auto Tab Discarder

> Last Updated: 2026-09-07

## Store Listing

**Extension Name** [REQUIRED]
Chrome RAM Saver & Auto Tab Discarder

**Short Description** [REQUIRED]
Libera memória RAM descartando abas inativas há mais de 20 minutos, limpando cache e otimizando a performance do Chrome.

**Detailed Description** [REQUIRED]
Chrome RAM Saver otimiza continuamente o uso de memória do Google Chrome sem fechar suas abas de trabalho.

Recursos principais:
- Descarte nativo de abas: Desaloca a memória RAM de abas ociosas sem fechá-las da barra. Ao clicar nelas, recarregam instantaneamente.
- Intervalo de inatividade configurável: Escolha suspender abas após 5, 10, 15, 20, 30 minutos ou 1 hora.
- Proteções inteligentes: Nunca suspende abas reproduzindo áudio (YouTube, Spotify, chamadas), abas fixadas ou a aba ativa atual.
- Lista de proteção (Whitelist): Proteja domínios importantes com apenas um clique.
- Limpeza de Cache de Rede: Limpa cache HTTP com segurança sem desconectar suas sessões ou apagar senhas.
- Fechador de Abas Duplicadas: Encontra e fecha abas idênticas em segundo plano.

Como usar:
1. Instale a extensão e fixe-a na barra de ferramentas.
2. O monitoramento automático entrará em ação com o tempo padrão de 20 minutos.
3. Clique no ícone a qualquer momento para ver quanta RAM foi poupada ou use o botão "Liberar Memória Agora".

Privacidade:
Esta extensão roda 100% localmente no seu navegador. Nenhum dado de navegação, URL ou informação pessoal é coletado ou transmitido para servidores externos.

**Category** [REQUIRED]
Productivity

**Single Purpose** [REQUIRED]
Suspende abas inativas e limpa cache de rede para liberar memória RAM e melhorar a performance do navegador.

**Primary Language** [REQUIRED]
Portuguese (Brazil)

## Graphics & Assets

| Asset | Dimensions | Status | Filename |
|-------|-----------|--------|----------|
| Store Icon [REQUIRED] | 128×128 PNG | ✅ Ready | icons/icon-128.png |
| Screenshot 1 [REQUIRED] | 1280×800 or 640×400 | ⬜ Not created | |
| Small Promo Tile [RECOMMENDED] | 440×280 | ⬜ Not created | |

## Permissions Justification

| Permission | Type | Justification |
|------------|------|---------------|
| `tabs` | permissions | Necessário para identificar o status das abas (ativa, fixada, reproduzindo som, inativa) e executar o descarte com `chrome.tabs.discard()`. |
| `storage` | permissions | Salva as preferências locais do usuário (tempo de inatividade, lista de sites protegidos e estatísticas locais). |
| `alarms` | permissions | Permite a execução da verificação em segundo plano em intervalos regulares para descartar abas inativas. |
| `browsingData` | permissions | Permite a limpeza do cache de rede HTTP e cache storage a pedido do usuário ou periodicamente. |

## Privacy & Data Use

**Does the extension collect user data?** No

### Data Use Certification
- [x] Data is NOT sold to third parties
- [x] Data is NOT used for purposes unrelated to the extension's core functionality
- [x] Data is NOT used for creditworthiness or lending purposes

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| 1.0.0 | 2026-09-07 | Versão inicial com descarte de abas (>20m), limpeza de cache e dashboard | Ready |
