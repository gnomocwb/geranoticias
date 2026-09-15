/**
 * =========================================================================================
 * 🩺 SISTEMA DE GESTÃO PARA CONSULTÓRIO DE FONOAUDIOLOGIA (GOOGLE SHEETS 100% NATIVO)
 * =========================================================================================
 * Autor: Google Antigravity
 * Versão: 1.0.0
 * 
 * INSTRUÇÕES RÁPIDAS:
 * 1. Crie uma planilha em branco no Google Sheets (sheets.new).
 * 2. Acesse: Extensões > Apps Script.
 * 3. Apague o código que estiver lá, cole este código completo e clique em "Salvar" (ícone de disquete).
 * 4. Na barra superior do Apps Script, selecione a função "setupPlanilhaCompleta" e clique em "Executar".
 * 5. Conceda as permissões de acesso solicitadas pelo Google.
 * 6. Volte na planilha: todas as abas, fórmulas, cores, validações e dados de exemplo estarão prontos!
 * =========================================================================================
 */

// Paleta de Cores Profissional para Saúde / Fonoaudiologia
const CORES = {
  HEADER_BG: "#1A365D",        // Azul Escuro Elegante
  HEADER_TEXT: "#FFFFFF",      // Branco
  ACCENT_TEAL: "#0D9488",      // Verde Petróleo / Saúde
  LIGHT_BG: "#F8FAFC",         // Cinza Gelo Neutro
  ALERT_YELLOW_BG: "#FEF7E0",  // Amarelo Alerta Suave
  ALERT_YELLOW_TXT: "#B06000",
  ALERT_RED_BG: "#FCE8E6",     // Vermelho Alerta
  ALERT_RED_TXT: "#C5221F",
  ALERT_GREEN_BG: "#E6F4EA",   // Verde Regular
  ALERT_GREEN_TXT: "#137333",
  BORDER_COLOR: "#CBD5E1"
};

/**
 * Cria o menu personalizado na barra superior do Google Sheets ao abrir
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("🩺 Gestão Fono")
    .addItem("📅 Gerar Agenda da Próxima Semana", "menuGerarAgendaSemanal")
    .addItem("⚠️ Verificar Alertas de Liminares", "menuVerificarLiminares")
    .addItem("🧾 Atualizar Painel de Notas Fiscais", "menuAtualizarPainelNF")
    .addSeparator()
    .addItem("🛠️ Configurar / Criar Abas Automaticamente", "setupPlanilhaCompleta")
    .addToUi();
}

/**
 * FUNÇÃO PRINCIPAL: Cria todas as abas, formatações, fórmulas e validações automaticamente!
 */
function setupPlanilhaCompleta() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Criar e configurar as abas
  const abaConfig = obterOuCriarAba(ss, "⚙️ Config");
  const abaPacientes = obterOuCriarAba(ss, "👤 Pacientes");
  const abaAtendimentos = obterOuCriarAba(ss, "📋 Atendimentos");
  const abaCheckin = obterOuCriarAba(ss, "📱 Check-in Hoje");
  const abaAgenda = obterOuCriarAba(ss, "📅 Agenda Semanal");
  const abaFinanceiro = obterOuCriarAba(ss, "💰 Financeiro");
  const abaNF = obterOuCriarAba(ss, "🧾 Gestão de NF");
  const abaDashboard = obterOuCriarAba(ss, "📊 Dashboard");

  // 2. Configurar Aba Configurações
  configurarAbaConfig(abaConfig);

  // 3. Configurar Aba Pacientes
  configurarAbaPacientes(abaPacientes, abaConfig);

  // 4. Configurar Aba Atendimentos
  configurarAbaAtendimentos(abaAtendimentos, abaPacientes, abaConfig);

  // 5. Configurar Aba Check-in Hoje
  configurarAbaCheckin(abaCheckin);

  // 6. Configurar Aba Financeiro
  configurarAbaFinanceiro(abaFinanceiro, abaConfig);

  // 7. Configurar Aba Gestão de NF
  configurarAbaNF(abaNF);

  // 8. Configurar Aba Dashboard
  configurarAbaDashboard(abaDashboard);

  // 9. Configurar Aba Agenda Semanal Visual
  configurarAbaAgendaSemanal(abaAgenda, abaPacientes);

  // Alerta de sucesso
  SpreadsheetApp.getUi().alert(
    "🎉 Sistema de Consultório Configurado com Sucesso!\n\n" +
    "Todas as 7 abas, regras de liminares, faturamento por sublocação e fórmulas foram instaladas.\n" +
    "Você já pode usar o menu '🩺 Gestão Fono' para automatizar sua rotina."
  );
}

/**
 * Auxiliar para obter aba existente ou criar nova
 */
function obterOuCriarAba(ss, nomeAba) {
  let aba = ss.getSheetByName(nomeAba);
  if (!aba) {
    aba = ss.insertSheet(nomeAba);
  }
  aba.clear();
  return aba;
}

/**
 * 2. Configura a Aba ⚙️ Config
 */
function configurarAbaConfig(aba) {
  aba.getRange("A1").setValue("⚙️ Parâmetros do Sistema").setFontWeight("bold").setFontSize(12);
  
  const colunas = [
    ["Vínculo", "Status Atendimento", "Categorias Despesas", "Dias da Semana", "Horários"],
    ["Particular", "Realizado", "Aluguel / Sublocação", "Segunda-feira", "08:00"],
    ["Liminar", "Falta Justificada", "Anuidade CRFa", "Terça-feira", "09:00"],
    ["Clínica Parceira", "Falta Injustificada", "Materiais Terapêuticos", "Quarta-feira", "10:00"],
    ["", "Desmarcado Antecipado", "Contabilidade", "Quinta-feira", "11:00"],
    ["", "", "Cursos & Supervisão", "Sexta-feira", "13:00"],
    ["", "", "Softwares / Telefonia", "Sábado", "14:00"],
    ["", "", "Outros", "", "15:00"],
    ["", "", "", "", "16:00"],
    ["", "", "", "", "17:00"],
    ["", "", "", "", "18:00"]
  ];
  
  aba.getRange(3, 1, colunas.length, colunas[0].length).setValues(colunas);
  formatarCabecalho(aba, 3, 1, colunas[0].length);
  aba.setTabColor("#64748B");
}

/**
 * 3. Configura a Aba 👤 Pacientes
 */
function configurarAbaPacientes(aba, abaConfig) {
  const headers = [
    "ID", "Nome do Paciente", "Responsável", "Telefone", "Tipo de Vínculo",
    "Dia Fixo", "Horário Fixo", "Valor Sessão (R$)", "Custo Sala / Repasse (R$)",
    "Contratadas (Liminar)", "Realizadas", "Saldo Restante", "Alerta Liminar",
    "Status Paciente", "CPF / CNPJ Tomador"
  ];
  
  aba.getRange(1, 1, 1, headers.length).setValues([headers]);
  formatarCabecalho(aba, 1, 1, headers.length);
  aba.setFrozenRows(1);

  // Dados de Exemplo Realistas
  const exemplos = [
    ["PAC-001", "Lucas Pereira (TEA)", "Mariana Pereira (Mãe)", "(41) 99111-2233", "Liminar", "Segunda-feira", "09:00", 180, 0, 40, '=IF(E2="Liminar"; COUNTIFS(📋 Atendimentos!D:D; B2; 📋 Atendimentos!G:G; "Realizado"); "-")', '=IF(E2="Liminar"; J2 - K2; "-")', '=IF(E2<>"Liminar"; "N/A"; IF(L2<=0; "🔴 ESGOTADO"; IF(L2<=2; "🔴 CRÍTICO (<= 2)"; IF(L2<=4; "🟡 ATENÇÃO (<= 4)"; "🟢 REGULAR"))))', "Ativo", "123.456.789-00"],
    ["PAC-002", "Enzo Gabriel", "Carlos Gabriel (Pai)", "(41) 99222-3344", "Particular", "Terça-feira", "10:00", 160, 35, "-", "-", "-", "N/A", "Ativo", "234.567.890-11"],
    ["PAC-003", "Beatriz Santos (Dislalia)", "Luciana Santos (Mãe)", "(41) 99333-4455", "Liminar", "Quarta-feira", "14:00", 180, 0, 20, '=IF(E4="Liminar"; COUNTIFS(📋 Atendimentos!D:D; B4; 📋 Atendimentos!G:G; "Realizado"); "-")', '=IF(E4="Liminar"; J4 - K4; "-")', '=IF(E4<>"Liminar"; "N/A"; IF(L4<=0; "🔴 ESGOTADO"; IF(L4<=2; "🔴 CRÍTICO (<= 2)"; IF(L4<=4; "🟡 ATENÇÃO (<= 4)"; "🟢 REGULAR"))))', "Ativo", "345.678.901-22"],
    ["PAC-004", "Alice Souza", "Própria", "(41) 99444-5566", "Clínica Parceira", "Quinta-feira", "15:00", 140, 56, "-", "-", "-", "N/A", "Ativo", "12.345.678/0001-90"],
    ["PAC-005", "Arthur Ramos (Apraxia)", "Juliana Ramos (Mãe)", "(41) 99555-6677", "Liminar", "Sexta-feira", "08:00", 180, 0, 10, '=IF(E6="Liminar"; COUNTIFS(📋 Atendimentos!D:D; B6; 📋 Atendimentos!G:G; "Realizado"); "-")', '=IF(E6="Liminar"; J6 - K6; "-")', '=IF(E6<>"Liminar"; "N/A"; IF(L6<=0; "🔴 ESGOTADO"; IF(L6<=2; "🔴 CRÍTICO (<= 2)"; IF(L6<=4; "🟡 ATENÇÃO (<= 4)"; "🟢 REGULAR"))))', "Ativo", "456.789.012-33"]
  ];

  aba.getRange(2, 1, exemplos.length, headers.length).setValues(exemplos);

  // Formatações de moeda
  aba.getRange("H2:I100").setNumberFormat("R$ #,##0.00");

  // Validações
  aplicarValidacaoLista(aba, "E2:E100", ["Particular", "Liminar", "Clínica Parceira"]);
  aplicarValidacaoLista(aba, "F2:F100", ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]);
  aplicarValidacaoLista(aba, "N2:N100", ["Ativo", "Em Pausa", "Encerrado"]);

  // Formatação Condicional de Alerta Liminar
  const rangeAlerta = aba.getRange("M2:M100");
  const ruleRed = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("🔴")
    .setBackground(CORES.ALERT_RED_BG)
    .setFontColor(CORES.ALERT_RED_TXT)
    .setBold(true)
    .setRanges([rangeAlerta])
    .build();

  const ruleYellow = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("🟡")
    .setBackground(CORES.ALERT_YELLOW_BG)
    .setFontColor(CORES.ALERT_YELLOW_TXT)
    .setBold(true)
    .setRanges([rangeAlerta])
    .build();

  const ruleGreen = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("🟢")
    .setBackground(CORES.ALERT_GREEN_BG)
    .setFontColor(CORES.ALERT_GREEN_TXT)
    .setRanges([rangeAlerta])
    .build();

  aba.setConditionalFormatRules([ruleRed, ruleYellow, ruleGreen]);
  aba.autoResizeColumns(1, headers.length);
  aba.setTabColor(CORES.ACCENT_TEAL);
}

/**
 * 4. Configura a Aba 📋 Atendimentos
 */
function configurarAbaAtendimentos(aba, abaPacientes, abaConfig) {
  const headers = [
    "Data", "Mês/Ano", "Horário", "Paciente", "Vínculo",
    "Valor Bruto", "Status Atendimento", "Cobrar?", "Custo Sala / Retenção",
    "Líquido Fono", "Status Financeiro", "Requer NF?", "Status NF", "Observações"
  ];

  aba.getRange(1, 1, 1, headers.length).setValues([headers]);
  formatarCabecalho(aba, 1, 1, headers.length);
  aba.setFrozenRows(1);

  // 10 Atendimentos de Exemplo
  const hoje = new Date();
  const formatarData = (d) => Utilities.formatDate(d, Session.getScriptTimeZone(), "dd/MM/yyyy");

  const atendExemplos = [];
  for (let i = 0; i < 8; i++) {
    const d = new Date(hoje);
    d.setDate(hoje.getDate() - (7 - i));
    const linha = i + 2;
    const pac = i % 2 === 0 ? "Lucas Pereira (TEA)" : (i % 3 === 0 ? "Enzo Gabriel" : "Arthur Ramos (Apraxia)");
    const status = i === 1 ? "Falta Justificada" : (i === 4 ? "Falta Injustificada" : "Realizado");

    atendExemplos.push([
      formatarData(d),
      `=TEXT(A${linha}; "mm/yyyy")`,
      "09:00",
      pac,
      `=IFERROR(VLOOKUP(D${linha}; '👤 Pacientes'!B:E; 4; FALSE); "")`,
      `=IFERROR(VLOOKUP(D${linha}; '👤 Pacientes'!B:H; 7; FALSE); 0)`,
      status,
      `=IF(OR(G${linha}="Realizado"; G${linha}="Falta Injustificada"); "SIM"; "NÃO")`,
      `=IF(H${linha}="SIM"; IF(E${linha}="Particular"; IFERROR(VLOOKUP(D${linha}; '👤 Pacientes'!B:I; 8; FALSE); 0); 0); 0)`,
      `=IF(H${linha}="SIM"; F${linha} - I${linha}; 0)`,
      status === "Realizado" ? "Recebido" : "Pendente",
      `=IF(AND(H${linha}="SIM"; E${linha}<>"Liminar"); "SIM"; "NÃO")`,
      status === "Realizado" ? (i % 2 === 0 ? "Emitida" : "Pendente") : "Não Aplicável",
      "Sessão regular"
    ]);
  }

  aba.getRange(2, 1, atendExemplos.length, headers.length).setValues(atendExemplos);

  // Formatações
  aba.getRange("F2:F100").setNumberFormat("R$ #,##0.00");
  aba.getRange("I2:J100").setNumberFormat("R$ #,##0.00");

  // Dropdowns
  aplicarValidacaoLista(aba, "G2:G500", ["Realizado", "Falta Justificada", "Falta Injustificada", "Desmarcado Antecipado"]);
  aplicarValidacaoLista(aba, "K2:K500", ["Recebido", "Pendente", "Faturado Pacote Liminar"]);
  aplicarValidacaoLista(aba, "M2:M500", ["Pendente", "Emitida", "Não Aplicável"]);

  // Formatação condicional de status de atendimento
  const rangeStatus = aba.getRange("G2:G500");
  const ruleRealizado = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo("Realizado")
    .setBackground(CORES.ALERT_GREEN_BG)
    .setFontColor(CORES.ALERT_GREEN_TXT)
    .setRanges([rangeStatus])
    .build();

  const ruleFalta = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("Falta")
    .setBackground(CORES.ALERT_RED_BG)
    .setFontColor(CORES.ALERT_RED_TXT)
    .setRanges([rangeStatus])
    .build();

  aba.setConditionalFormatRules([ruleRealizado, ruleFalta]);
  aba.autoResizeColumns(1, headers.length);
  aba.setTabColor(CORES.HEADER_BG);
}

/**
 * 5. Configura a Aba 📱 Check-in Hoje (Otimizada para Celular)
 */
function configurarAbaCheckin(aba) {
  aba.getRange("A1").setValue("📱 Atendimentos de Hoje").setFontWeight("bold").setFontSize(14).setFontColor(CORES.HEADER_BG);
  aba.getRange("A2").setValue("Marque os status diretamente abaixo durante o dia de atendimento:").setFontStyle("italic").setFontColor("#64748B");

  const headers = ["Horário", "Paciente", "Vínculo", "Status Atendimento", "Status Financeiro", "Observações"];
  aba.getRange(4, 1, 1, headers.length).setValues([headers]);
  formatarCabecalho(aba, 4, 1, headers.length);
  aba.setFrozenRows(4);

  // Fórmula Query dinâmica que traz tudo do dia de hoje
  aba.getRange("A5").setFormula(
    '=IFERROR(QUERY(\'📋 Atendimentos\'!A:N; "SELECT C, D, E, G, K, N WHERE A = date \'" & TEXT(TODAY(); "yyyy-mm-dd") & "\' ORDER BY C ASC LABEL C \'\', D \'\', E \'\', G \'\', K \'\', N \'\'"); {"Nenhum atendimento agendado para hoje."; ""; ""; ""; ""; ""})'
  );

  aba.setColumnWidth(1, 90);
  aba.setColumnWidth(2, 220);
  aba.setColumnWidth(3, 130);
  aba.setColumnWidth(4, 180);
  aba.setColumnWidth(5, 140);
  aba.setColumnWidth(6, 250);
  aba.setTabColor("#2563EB");
}

/**
 * 6. Configura a Aba 💰 Financeiro
 */
function configurarAbaFinanceiro(aba, abaConfig) {
  aba.getRange("A1").setValue("💰 Fluxo de Caixa do Consultório").setFontWeight("bold").setFontSize(14).setFontColor(CORES.HEADER_BG);

  // Cards de Resumo no topo
  aba.getRange("A3").setValue("Receitas do Mês Atual (Agenda):").setFontWeight("bold");
  aba.getRange("B3").setFormula('=SUMIFS(\'📋 Atendimentos\'!J:J; \'📋 Atendimentos\'!B:B; TEXT(TODAY(); "mm/yyyy"); \'📋 Atendimentos\'!H:H; "SIM")').setNumberFormat("R$ #,##0.00").setFontWeight("bold").setFontColor(CORES.ALERT_GREEN_TXT);

  aba.getRange("D3").setValue("Despesas do Mês Atual:").setFontWeight("bold");
  aba.getRange("E3").setFormula('=SUMIFS(D7:D100; B7:B100; TEXT(TODAY(); "mm/yyyy"); E7:E100; "Pago")').setNumberFormat("R$ #,##0.00").setFontWeight("bold").setFontColor(CORES.ALERT_RED_TXT);

  aba.getRange("G3").setValue("Resultado Líquido do Mês:").setFontWeight("bold");
  aba.getRange("H3").setFormula('=B3 - E3').setNumberFormat("R$ #,##0.00").setFontWeight("bold").setFontSize(12);

  // Tabela de Despesas
  const headers = ["Data", "Mês/Ano", "Categoria", "Valor (R$)", "Status", "Descrição / Fornecedor"];
  aba.getRange(6, 1, 1, headers.length).setValues([headers]);
  formatarCabecalho(aba, 6, 1, headers.length);
  aba.setFrozenRows(6);

  const hoje = new Date();
  const formatarData = (d) => Utilities.formatDate(d, Session.getScriptTimeZone(), "dd/MM/yyyy");

  const despesasExemplo = [
    [formatarData(hoje), `=TEXT(A7; "mm/yyyy")`, "Aluguel / Sublocação", 600, "Pago", "Sublocação de sala - pacote mensal"],
    [formatarData(hoje), `=TEXT(A8; "mm/yyyy")`, "Materiais Terapêuticos", 150, "Pago", "Brinquedos pedagógicos e espátulas descartáveis"],
    [formatarData(hoje), `=TEXT(A9; "mm/yyyy")`, "Anuidade CRFa", 85, "Pago", "Parcela da anuidade do conselho"],
    [formatarData(hoje), `=TEXT(A10; "mm/yyyy")`, "Contabilidade", 200, "A Pagar", "Honorários mensais da contabilidade"]
  ];

  aba.getRange(7, 1, despesasExemplo.length, headers.length).setValues(despesasExemplo);
  aba.getRange("D7:D100").setNumberFormat("R$ #,##0.00");
  aplicarValidacaoLista(aba, "C7:C100", ["Aluguel / Sublocação", "Anuidade CRFa", "Materiais Terapêuticos", "Contabilidade", "Cursos & Supervisão", "Softwares / Telefonia", "Outros"]);
  aplicarValidacaoLista(aba, "E7:E100", ["Pago", "A Pagar"]);

  aba.autoResizeColumns(1, headers.length);
  aba.setTabColor("#059669");
}

/**
 * 7. Configura a Aba 🧾 Gestão de NF
 */
function configurarAbaNF(aba) {
  aba.getRange("A1").setValue("🧾 Painel de Emissão de Notas Fiscais").setFontWeight("bold").setFontSize(14).setFontColor(CORES.HEADER_BG);
  aba.getRange("A2").setValue("Selecione o Mês/Ano de Referência:").setFontWeight("bold");
  aba.getRange("C2").setValue("09/2026").setFontWeight("bold").setBackground(CORES.ALERT_YELLOW_BG);

  const headers = ["Tomador (Paciente / Clínica)", "Tipo Vínculo", "Valor Total a Emitir", "Qtd Sessões", "Emitida?", "Nº da Nota Fiscal"];
  aba.getRange(4, 1, 1, headers.length).setValues([headers]);
  formatarCabecalho(aba, 4, 1, headers.length);
  aba.setFrozenRows(4);

  // Fórmula consolidada automática
  aba.getRange("A5").setFormula(
    '=IFERROR(QUERY(\'📋 Atendimentos\'!A:N; "SELECT D, E, SUM(F), COUNT(G) WHERE B = \'" & C2 & "\' AND H = \'SIM\' AND L = \'SIM\' GROUP BY D, E LABEL D \'\', E \'\', SUM(F) \'\', COUNT(G) \'\'"); {"Nenhum faturamento particular/clínica com NF pendente para este mês."; ""; ""; ""})'
  );

  aba.getRange("C5:C50").setNumberFormat("R$ #,##0.00");
  aba.getRange("E5:E50").insertCheckboxes();

  aba.setColumnWidth(1, 260);
  aba.setColumnWidth(2, 160);
  aba.setColumnWidth(3, 160);
  aba.setColumnWidth(4, 110);
  aba.setColumnWidth(5, 90);
  aba.setColumnWidth(6, 150);
  aba.setTabColor("#D97706");
}

/**
 * 8. Configura a Aba 📊 Dashboard
 */
function configurarAbaDashboard(aba) {
  aba.getRange("A1").setValue("📊 Painel Executivo do Consultório").setFontWeight("bold").setFontSize(16).setFontColor(CORES.HEADER_BG);
  aba.getRange("A2").setValue("Mês Selecionado:").setFontWeight("bold");
  aba.getRange("B2").setValue("09/2026").setFontWeight("bold").setBackground(CORES.ALERT_YELLOW_BG);

  // Cards de Indicadores
  const kpis = [
    ["Faturamento Bruto", "=SUMIFS('📋 Atendimentos'!F:F; '📋 Atendimentos'!B:B; B2; '📋 Atendimentos'!H:H; \"SIM\")"],
    ["Custos Sublocação Sala", "=SUMIFS('📋 Atendimentos'!I:I; '📋 Atendimentos'!B:B; B2; '📋 Atendimentos'!H:H; \"SIM\")"],
    ["Despesas Operacionais", "=SUMIFS('💰 Financeiro'!D:D; '💰 Financeiro'!B:B; B2)"],
    ["LUCRO LÍQUIDO", "=B4 - B5 - B6"],
    ["Taxa de Faltas", "=IFERROR(COUNTIFS('📋 Atendimentos'!B:B; B2; '📋 Atendimentos'!G:G; \"*Falta*\") / COUNTIF('📋 Atendimentos'!B:B; B2); 0)"],
    ["Liminares em Alerta", "=COUNTIFS('👤 Pacientes'!E:E; \"Liminar\"; '👤 Pacientes'!M:M; \"*CRÍTICO*\") + COUNTIFS('👤 Pacientes'!E:E; \"Liminar\"; '👤 Pacientes'!M:M; \"*ATENÇÃO*\")"]
  ];

  for (let i = 0; i < kpis.length; i++) {
    const linha = i + 4;
    aba.getRange(linha, 1).setValue(kpis[i][0]).setFontWeight("bold").setBackground(CORES.LIGHT_BG);
    const cellVal = aba.getRange(linha, 2).setFormula(kpis[i][1]).setFontWeight("bold").setFontSize(11);
    
    if (i < 4) {
      cellVal.setNumberFormat("R$ #,##0.00");
    } else if (i === 4) {
      cellVal.setNumberFormat("0.0%");
    }
  }

  // Destaque visual no Lucro Líquido
  aba.getRange("A7:B7").setBackground("#DCFCE7").setFontColor("#14532D").setFontSize(12);

  aba.setColumnWidth(1, 220);
  aba.setColumnWidth(2, 160);
  aba.setTabColor("#7C3AED");
}

/**
 * 9. Configura a Aba 📅 Agenda Semanal
 */
function configurarAbaAgendaSemanal(aba, abaPacientes) {
  aba.getRange("A1").setValue("📅 Grade Semanal do Consultório").setFontWeight("bold").setFontSize(14).setFontColor(CORES.HEADER_BG);
  
  const dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];
  const horarios = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"];

  aba.getRange(3, 1).setValue("Horário");
  for (let d = 0; d < dias.length; d++) {
    aba.getRange(3, d + 2).setValue(dias[d]);
  }
  formatarCabecalho(aba, 3, 1, dias.length + 1);

  for (let h = 0; h < horarios.length; h++) {
    aba.getRange(h + 4, 1).setValue(horarios[h]).setFontWeight("bold").setBackground(CORES.LIGHT_BG);
  }

  // Preenche células com fórmula LOOKUP para puxar o paciente fixo cadastrado
  for (let h = 0; h < horarios.length; h++) {
    const hora = horarios[h];
    for (let d = 0; d < dias.length; d++) {
      const dia = dias[d];
      const cell = aba.getRange(h + 4, d + 2);
      cell.setFormula(
        `=IFERROR(INDEX('👤 Pacientes'!B:B; MATCH(1; ('👤 Pacientes'!F:F="${dia}") * ('👤 Pacientes'!G:G="${hora}") * ('👤 Pacientes'!N:N="Ativo"); 0)); "-")`
      );
    }
  }

  aba.setColumnWidth(1, 80);
  for (let c = 2; c <= 7; c++) {
    aba.setColumnWidth(c, 160);
  }
  aba.setTabColor("#0284C7");
}

/**
 * Função utilitária para padronizar cabeçalhos
 */
function formatarCabecalho(aba, linha, colInicio, numCols) {
  const range = aba.getRange(linha, colInicio, 1, numCols);
  range.setBackground(CORES.HEADER_BG)
       .setFontColor(CORES.HEADER_TEXT)
       .setFontWeight("bold")
       .setFontSize(10)
       .setVerticalAlignment("middle");
  aba.setRowHeight(linha, 32);
}

/**
 * Função utilitária para aplicar validação de lista suspensa
 */
function aplicarValidacaoLista(aba, rangeA1, lista) {
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(lista, true)
    .setAllowInvalid(false)
    .build();
  aba.getRange(rangeA1).setDataValidation(rule);
}

/**
 * ---------------------------------------------------------------------------------
 * AÇÕES DO MENU DE AUTOMAÇÃO
 * ---------------------------------------------------------------------------------
 */

/**
 * Gera os atendimentos da semana na aba 📋 Atendimentos com base nos pacientes ativos
 */
function menuGerarAgendaSemanal() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const abaPac = ss.getSheetByName("👤 Pacientes");
  const abaAtend = ss.getSheetByName("📋 Atendimentos");

  const resposta = ui.prompt(
    "Gerar Agenda Semanal",
    "Digite a data de início da semana (Segunda-feira) no formato DD/MM/AAAA:",
    ui.ButtonSet.OK_CANCEL
  );

  if (resposta.getSelectedButton() !== ui.Button.OK) return;
  const dataStr = resposta.getResponseText().trim();
  const partes = dataStr.split("/");
  if (partes.length !== 3) {
    ui.alert("Formato inválido! Use DD/MM/AAAA.");
    return;
  }

  const dataSegunda = new Date(parseInt(partes[2]), parseInt(partes[1]) - 1, parseInt(partes[0]));
  const mapaDias = {
    "Segunda-feira": 0,
    "Terça-feira": 1,
    "Quarta-feira": 2,
    "Quinta-feira": 3,
    "Sexta-feira": 4,
    "Sábado": 5
  };

  const dadosPacientes = abaPac.getRange("A2:N" + abaPac.getLastRow()).getValues();
  const novosAtendimentos = [];

  for (let i = 0; i < dadosPacientes.length; i++) {
    const nome = dadosPacientes[i][1];
    const dia = dadosPacientes[i][5];
    const hora = dadosPacientes[i][6];
    const statusPac = dadosPacientes[i][13];

    if (statusPac === "Ativo" && dia && hora && mapaDias.hasOwnProperty(dia)) {
      const dataSessao = new Date(dataSegunda);
      dataSessao.setDate(dataSegunda.getDate() + mapaDias[dia]);
      const dataFormatada = Utilities.formatDate(dataSessao, Session.getScriptTimeZone(), "dd/MM/yyyy");
      const linha = abaAtend.getLastRow() + novosAtendimentos.length + 1;

      novosAtendimentos.push([
        dataFormatada,
        `=TEXT(A${linha}; "mm/yyyy")`,
        hora,
        nome,
        `=IFERROR(VLOOKUP(D${linha}; '👤 Pacientes'!B:E; 4; FALSE); "")`,
        `=IFERROR(VLOOKUP(D${linha}; '👤 Pacientes'!B:H; 7; FALSE); 0)`,
        "Agendado",
        `=IF(OR(G${linha}="Realizado"; G${linha}="Falta Injustificada"); "SIM"; "NÃO")`,
        `=IF(H${linha}="SIM"; IF(E${linha}="Particular"; IFERROR(VLOOKUP(D${linha}; '👤 Pacientes'!B:I; 8; FALSE); 0); 0); 0)`,
        `=IF(H${linha}="SIM"; F${linha} - I${linha}; 0)`,
        "Pendente",
        `=IF(AND(H${linha}="SIM"; E${linha}<>"Liminar"); "SIM"; "NÃO")`,
        "Pendente",
        ""
      ]);
    }
  }

  if (novosAtendimentos.length > 0) {
    const linhaDestino = abaAtend.getLastRow() + 1;
    abaAtend.getRange(linhaDestino, 1, novosAtendimentos.length, novosAtendimentos[0].length).setValues(novosAtendimentos);
    ui.alert(`✓ ${novosAtendimentos.length} atendimentos gerados com sucesso para a semana de ${dataStr}!`);
  } else {
    ui.alert("Nenhum paciente ativo com dia e horário fixo encontrado.");
  }
}

/**
 * Verifica pacientes por liminar com menos de 4 sessões restantes e alerta
 */
function menuVerificarLiminares() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const abaPac = ss.getSheetByName("👤 Pacientes");
  const dados = abaPac.getRange("B2:M" + abaPac.getLastRow()).getValues();

  const alertas = [];
  for (let i = 0; i < dados.length; i++) {
    const nome = dados[i][0];
    const tipo = dados[i][3];
    const saldo = dados[i][10];
    const alerta = dados[i][11];

    if (tipo === "Liminar" && typeof saldo === "number" && saldo <= 4) {
      alertas.push(`• ${nome}: Restam apenas ${saldo} sessões! (${alerta})`);
    }
  }

  if (alertas.length > 0) {
    ui.alert("⚠️ Atenção: Pacientes com Liminar Próxima do Fim:\n\n" + alertas.join("\n"));
  } else {
    ui.alert("🟢 Regular: Todas as liminares estão com mais de 4 sessões disponíveis.");
  }
}

/**
 * Atualiza o seletor da aba de Gestão de Notas Fiscais
 */
function menuAtualizarPainelNF() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const abaNF = ss.getSheetByName("🧾 Gestão de NF");
  const mesAtual = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "MM/yyyy");
  abaNF.getRange("C2").setValue(mesAtual);
  SpreadsheetApp.getActiveSpreadsheet().toast("Painel atualizado para o mês " + mesAtual, "🧾 Gestão de NF", 3);
}
