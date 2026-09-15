# 📘 Guia de Implantação e Uso do Sistema para Consultório de Fonoaudiologia

Este guia explica como instalar e utilizar a solução **100% nativa no Google Sheets**, criada sob medida para profissionais da fonoaudiologia com atendimentos recorrentes, liminares e sublocação.

---

## ⚡ 1. Instalação Automática em 2 Minutos

Não é necessário formatar coluna por coluna manualmente. O script preparado monta todo o sistema automaticamente:

1. Acesse [sheets.new](https://sheets.new) no seu navegador para abrir uma nova planilha do Google em branco.
2. Nomeie a planilha como: **`Gestão de Consultório — Fonoaudiologia`**.
3. No menu superior, clique em: **Extensões** > **Apps Script**.
4. Apague todo o código que estiver na tela do editor.
5. Abra o arquivo [`setup_planilha.js`](setup_planilha.js), copie todo o seu conteúdo e cole no editor do Apps Script.
6. Clique no ícone de disquete (**Salvar projeto**) ou aperte `Ctrl + S`.
7. Na barra superior do Apps Script, verifique se a função selecionada é **`setupPlanilhaCompleta`** e clique em **Executar** (`▶`).
8. O Google solicitará uma autorização de segurança padrão (clique em *Revisar permissões* > selecione sua conta > *Avançado* > *Acessar projeto*).
9. Volte para a aba da planilha: **todas as 7 abas, cores, validações, fórmulas e dados de exemplo já estarão prontos e funcionando!**

---

## 🧭 2. Como Funciona no Dia a Dia

### 👤 2.1. Cadastro de Pacientes (`👤 Pacientes`)
- Cadastre cada paciente uma única vez com seu **Dia Fixo** e **Horário Fixo**.
- Escolha o **Tipo de Vínculo**:
  - **Particular:** informe o valor da sessão e o custo da sala de sublocação. O sistema deduzirá esse valor automaticamente a cada sessão realizada.
  - **Liminar:** informe a quantidade total de sessões contratadas pelo pacote ou ordem judicial (ex: `40`). O saldo e o alerta de renovação serão atualizados sozinhos.
  - **Clínica Parceira:** informe o valor do repasse e o CNPJ da clínica.

### ⚠️ 2.2. Alerta Inteligente de Liminares
A coluna **Saldo Restante** diminui automaticamente conforme os atendimentos são marcados como *Realizado*:
- **🟡 Amarelo:** Quando restarem **4 sessões** (*Atenção: preparar relatório de renovação*).
- **🔴 Vermelho:** Quando restarem **2 ou menos sessões** (*Crítico: prazo de vigência*).
- **🔴 Vermelho Escuro:** Saldo zero (*Esgotado*).
- Você também pode clicar no menu superior **`🩺 Gestão Fono` > `⚠️ Verificar Alertas de Liminares`** para ver um resumo em pop-up com um clique.

### 📱 2.3. Uso Rápido no Celular (`📱 Check-in Hoje`)
No aplicativo do Google Sheets no smartphone:
1. Abra diretamente a primeira aba: **`📱 Check-in Hoje`**.
2. Ela exibe exclusivamente os pacientes agendados para o dia de hoje em formato de lista vertical espaçada.
3. Conforme o paciente entrar na sala ou faltar, toque no menu suspenso de status:
   - **`Realizado`**: abate da liminar e contabiliza receita no financeiro.
   - **`Falta Justificada`**: registra a taxa de faltas sem cobrar do paciente.
   - **`Falta Injustificada`**: cobra a sessão conforme regra contratual e registra absenteísmo.
   - **`Desmarcado Antecipado`**: não gera cobrança nem desconta pacote.

### 📅 2.4. Gerando a Agenda da Nova Semana
No computador, ao início de cada semana:
1. Clique no menu superior: **`🩺 Gestão Fono` > `📅 Gerar Agenda da Próxima Semana`**.
2. Digite a data da segunda-feira (ex: `21/09/2026`).
3. O sistema varre todos os seus pacientes com status *Ativo*, calcula as datas de cada dia e cria os agendamentos da semana inteira na aba `📋 Atendimentos` e na grade visual da aba `📅 Agenda Semanal`.

### 🧾 2.5. Fechamento de Mês e Notas Fiscais (`🧾 Gestão de NF`)
No fim do ciclo mensal:
1. Acesse a aba **`🧾 Gestão de NF`**.
2. O seletor `C2` consolida automaticamente quem precisa de Nota Fiscal:
   - Pacientes particulares (com o valor total de sessões faturadas no mês e CPF).
   - Clínicas parceiras (com o total de repasses a receber no mês e CNPJ).
3. Conforme você emitir no portal da Prefeitura, marque a caixa de seleção `[x]` e anote o número da NF emitida.

### 💰 2.6. Fluxo de Caixa e Despesas (`💰 Financeiro`)
- **Entradas:** são alimentadas de forma 100% automática a partir dos atendimentos marcados como *Realizado* (já deduzindo custos de sala).
- **Saídas:** registre suas despesas operacionais do mês (Aluguel, Anuidade do CRFa, compra de materiais lúdicos, contabilidade).
- O cabeçalho exibe o **Resultado Líquido Real** em tempo real.

---

## 🔒 3. Proteção e Bloqueio de Fórmulas

Para garantir que fórmulas não sejam apagadas por engano:

1. Na aba **`📋 Atendimentos`**:
   - As colunas **B (Mês/Ano)**, **E (Vínculo)**, **F (Valor Bruto)**, **H (Cobrar?)**, **I (Custo Sala)**, **J (Líquido)** e **L (Requer NF?)** contêm fórmulas automáticas.
   - Para protegê-las: Selecione as colunas com fórmulas > Clique com botão direito > **Ver mais ações da célula** > **Proteger intervalo** > Clique em *Definir permissões* e marque apenas você como editor.
2. Na aba **`👤 Pacientes`**:
   - As colunas **K (Realizadas)**, **L (Saldo)** e **M (Alerta)** devem permanecer protegidas.
3. As abas **`📊 Dashboard`** e **`📱 Check-in Hoje`** podem ser protegidas por inteiro, pois são geradas por fórmulas analíticas.
