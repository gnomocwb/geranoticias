# 🩺 Sistema de Gestão para Consultório de Fonoaudiologia (Google Sheets 100% Nativo)

Especificação técnica, regras de negócio, colunas e fórmulas prontas para implementação da solução personalizada no Google Sheets.

---

## 📑 1. Estrutura de Abas da Planilha

A planilha é organizada em **7 abas estratégicas**, separando claramente o cadastro, a operação diária, a consolidação financeira e a inteligência visual:

| Aba | Finalidade | Nível de Acesso do Usuário |
| :--- | :--- | :--- |
| **`📱 Check-in Hoje`** | Visão vertical rápida para registrar atendimentos do dia pelo celular | **Edição diária** (apenas coluna de status) |
| **`📅 Agenda Semanal`** | Painel visual da semana com grade por horários | **Edição semanal** e conferência |
| **`📋 Atendimentos`** | Banco de dados central com histórico de todas as sessões do ano | **Automático / Edição controlada** |
| **`👤 Pacientes`** | Cadastro de pacientes, regras de cobrança e saldo de liminares | **Edição cadastral** |
| **`💰 Financeiro`** | Fluxo de caixa com entradas automáticas e despesas manuais | **Edição de despesas** |
| **`🧾 Gestão de NF`** | Painel mensal de emissão de Notas Fiscais com checklists | **Edição de status de NF** |
| **`📊 Dashboard`** | Indicadores gráficos de faturamento, lucro e faltas | **Visualização pura (Protegido)** |
| **`⚙️ Config`** | Listas suspensas, parâmetros de clínicas e custos de salas | **Apenas configuração inicial** |

---

## 👤 2. Aba: `Pacientes` (Cadastro & Regras Contratuais)

Esta aba armazena os dados do paciente e calcula dinamicamente o saldo de liminares.

### Colunas:
- **A: ID** (ex: `PAC-001`, `PAC-002`)
- **B: Nome do Paciente**
- **C: Nome do Responsável** *(se menor de idade)*
- **D: Telefone / WhatsApp**
- **E: Tipo de Vínculo** *(Dropdown: `Particular`, `Liminar`, `Clínica Parceira`)*
- **F: Dia Fixo** *(Dropdown: `Segunda-feira`, `Terça-feira`, `Quarta-feira`, `Quinta-feira`, `Sexta-feira`, `Sábado`)*
- **G: Horário Fixo** *(ex: `08:00`, `09:00`, `14:00`)*
- **H: Valor por Sessão (R$)**
- **I: Regra de Sublocação / Repasse**:
  - Se Particular: Taxa fixa de sala (R$) ou percentual retido pela sala.
  - Se Clínica: Percentual de repasse que a clínica paga (ex: 60%).
- **J: Sessões Contratadas (Liminar)** *(Qtd total de sessões do pacote/ordem judicial)*
- **K: Sessões Realizadas** *(Calculado automaticamente via fórmula)*
- **L: Saldo de Sessões Restantes** *(Calculado automaticamente)*
- **M: Alerta Liminar** *(Sinalizador visual)*
- **N: Status do Cadastro** *(Dropdown: `Ativo`, `Em Pausa`, `Encerrado`)*
- **O: CPF / CNPJ para Nota Fiscal**

### Fórmulas da Aba `Pacientes`:
- **Sessões Realizadas (Coluna K, linha 2):**
  ```excel
  =IF(E2="Liminar"; COUNTIFS(Atendimentos!D:D; B2; Atendimentos!G:G; "Realizado"); "-")
  ```
- **Saldo de Sessões (Coluna L, linha 2):**
  ```excel
  =IF(E2="Liminar"; J2 - K2; "-")
  ```
- **Alerta Liminar (Coluna M, linha 2):**
  ```excel
  =IF(E2<>"Liminar"; "N/A"; IF(L2<=0; "🔴 ESGOTADO"; IF(L2<=2; "🔴 CRÍTICO (<= 2)"; IF(L2<=4; "🟡 ATENÇÃO (<= 4)"; "🟢 REGULAR"))))
  ```

### Formatação Condicional no Saldo / Alerta:
- Se contiver `"🔴"`: Preenchimento vermelho claro `#FCE8E6`, texto vermelho escuro `#C5221F`, negrito.
- Se contiver `"🟡"`: Preenchimento amarelo claro `#FEF7E0`, texto amarelo escuro `#B06000`, negrito.
- Se contiver `"🟢"`: Preenchimento verde claro `#E6F4EA`, texto verde escuro `#137333`.

---

## 📋 3. Aba: `Atendimentos` (Banco de Dados de Sessões)

Alimentada automaticamente pelo script da agenda semanal ou preenchida diretamente. É o motor que calcula receitas, custos e faturamentos.

### Colunas:
- **A: Data** (`DD/MM/AAAA`)
- **B: Mês/Ano** *(Fórmula: `=TEXT(A2; "mm/yyyy")`)*
- **C: Horário**
- **D: Paciente** *(Dropdown vinculado aos ativos de `Pacientes`)*
- **E: Tipo de Vínculo** *(Fórmula: `=IFERROR(VLOOKUP(D2; Pacientes!B:E; 4; FALSE); "")`)*
- **F: Valor Bruto Sessão** *(Fórmula: `=IFERROR(VLOOKUP(D2; Pacientes!B:H; 7; FALSE); 0)`)*
- **G: Status do Atendimento** *(Dropdown: `Realizado`, `Falta Justificada`, `Falta Injustificada`, `Desmarcado Antecipado`)*
- **H: Cobrar Sessão?** *(Fórmula condicional)*:
  ```excel
  =IF(OR(G2="Realizado"; G2="Falta Injustificada"); "SIM"; "NÃO")
  ```
- **I: Custo Sala / Retenção Sublocação (R$)**:
  ```excel
  =IF(H2="SIM"; IF(E2="Particular"; IFERROR(VLOOKUP(D2; Pacientes!B:I; 8; FALSE); 0); 0); 0)
  ```
- **J: Faturamento Líquido Profissional (R$)**:
  ```excel
  =IF(H2="SIM"; F2 - I2; 0)
  ```
- **K: Status Financeiro** *(Dropdown: `Recebido`, `Pendente`, `Faturado Pacote Liminar`)*
- **L: Requer Nota Fiscal?** *(Fórmula: `=IF(AND(H2="SIM"; E2<>"Liminar"); "SIM"; "NÃO")`)*
- **M: Status NF** *(Dropdown: `Pendente`, `Emitida`, `Não Aplicável`)*
- **N: Observações / Evolução Rápida**

---

## 📱 4. Aba: `Check-in Hoje` (Otimizada para Celular)

Uma visão vertical ultraleve, exibindo apenas as sessões da data atual (`TODAY()`), com linha espaçada para toque fácil no smartphone:

```excel
=QUERY(
  Atendimentos!A:N;
  "SELECT C, D, E, G, K, N 
   WHERE A = date '" & TEXT(TODAY(); "yyyy-mm-dd") & "' 
   ORDER BY C ASC 
   LABEL C 'Horário', D 'Paciente', E 'Vínculo', G 'Status Atendimento', K 'Financeiro', N 'Obs'"
)
```

---

## 💰 5. Aba: `Financeiro` (Fluxo de Caixa)

Consolida receitas operacionais automáticas e despesas da profissional:

### Entradas (Automatizadas via Agenda):
Receitas calculadas por mês:
```excel
=SUMIFS(Atendimentos!J:J; Atendimentos!B:B; B1; Atendimentos!H:H; "SIM")
```

### Saídas (Despesas Operacionais):
- **Data**
- **Categoria** *(Dropdown: `Aluguel / Sublocação`, `Anuidade CRP/CRFa`, `Materiais Terapêuticos / Brinquedos`, `Contabilidade`, `Cursos & Supervisão`, `Softwares / Telefonia`, `Outros`)*
- **Descrição** (ex: "Compra de jogos de estimulação fonoaudiológica")
- **Valor (R$)**
- **Status** (`Pago`, `A Pagar`)

---

## 🧾 6. Aba: `Gestão de NF` (Painel Fiscal Mensal)

Lista exatamente quem precisa de Nota Fiscal no mês selecionado:

- Célula `B1`: Seletor do Mês/Ano (ex: `09/2026`).

### Tabela Consolidada por Tomador:
```excel
=QUERY(
  Atendimentos!A:N;
  "SELECT D, E, SUM(F), COUNT(G) 
   WHERE B = '" & B1 & "' AND H = 'SIM' AND L = 'SIM' 
   GROUP BY D, E 
   LABEL D 'Tomador do Serviço (Paciente / Clínica)', E 'Tipo', SUM(F) 'Valor Total a Emitir (R$)', COUNT(G) 'Qtd Sessões'"
)
```

---

## 📊 7. Aba: `Dashboard` (Painel Visual)

### Indicadores Principais (KPIs do Mês de Referência):
1. **Faturamento Bruto**: `=SUMIFS(Atendimentos!F:F; Atendimentos!B:B; B1; Atendimentos!H:H; "SIM")`
2. **Custos de Sublocação de Sala**: `=SUMIFS(Atendimentos!I:I; Atendimentos!B:B; B1; Atendimentos!H:H; "SIM")`
3. **Despesas Operacionais Fixas/Variáveis**: `=SUMIFS(Financeiro!D:D; Financeiro!A:A; ">="&DATE(YEAR(TODAY()); MONTH(TODAY()); 1))`
4. **Lucro Líquido Real**: `=Faturamento_Bruto - Custos_Sublocacao - Despesas_Operacionais`
5. **Taxa de Absenteísmo (Faltas)**:
   ```excel
   =COUNTIFS(Atendimentos!B:B; B1; Atendimentos!G:G; "*Falta*") / IFERROR(COUNTIF(Atendimentos!B:B; B1); 1)
   ```
6. **Alertas de Liminares**:
   ```excel
   =COUNTIFS(Pacientes!E:E; "Liminar"; Pacientes!M:M; "*CRÍTICO*") + COUNTIFS(Pacientes!E:E; "Liminar"; Pacientes!M:M; "*ATENÇÃO*")
   ```
