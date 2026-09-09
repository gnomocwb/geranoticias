/**
 * Chrome RAM Saver - Popup Controller
 */

// Estado local
let appState = {
  settings: {
    inactivityMinutes: 20,
    autoDiscardEnabled: true,
    protectAudible: true,
    protectPinned: true,
    autoClearCache: false,
    autoCloseDuplicates: false,
    cacheIntervalHours: 24,
    whitelist: []
  },
  stats: {
    totalTabs: 0,
    discardedTabs: 0,
    activeTabs: 0,
    audibleTabs: 0,
    duplicateCount: 0,
    currentSavedMB: 0,
    totalDiscardedLifetime: 0,
    totalCacheCleans: 0,
    lastCacheCleanTimestamp: null
  },
  activeHostname: ""
};

// Elementos DOM
const elRamSaved = document.getElementById("ramSaved");
const elRamDetail = document.getElementById("ramDetail");
const elDiscardedTabs = document.getElementById("discardedTabs");
const elTotalTabs = document.getElementById("totalTabs");
const elProgressBar = document.getElementById("tabProgressBar");
const elToast = document.getElementById("toast");

const btnDiscardNow = document.getElementById("btnDiscardNow");
const btnClearCache = document.getElementById("btnClearCache");
const btnCloseDuplicates = document.getElementById("btnCloseDuplicates");
const closeDuplicatesText = document.getElementById("closeDuplicatesText");
const btnRefresh = document.getElementById("btnRefresh");

const timePresets = document.getElementById("timePresets");
const inactivityHint = document.getElementById("inactivityHint");

const toggleAutoDiscard = document.getElementById("toggleAutoDiscard");
const toggleAutoCloseDuplicates = document.getElementById("toggleAutoCloseDuplicates");
const toggleProtectAudible = document.getElementById("toggleProtectAudible");
const toggleProtectPinned = document.getElementById("toggleProtectPinned");
const toggleAutoCache = document.getElementById("toggleAutoCache");

const quickProtectContainer = document.getElementById("quickProtectContainer");
const btnProtectCurrentTab = document.getElementById("btnProtectCurrentTab");
const protectCurrentText = document.getElementById("protectCurrentText");
const addDomainForm = document.getElementById("addDomainForm");
const domainInput = document.getElementById("domainInput");
const whitelistTags = document.getElementById("whitelistTags");

const statLifetimeDiscarded = document.getElementById("statLifetimeDiscarded");
const statCacheCleans = document.getElementById("statCacheCleans");
const statLastCacheClean = document.getElementById("statLastCacheClean");
const statAudibleTabs = document.getElementById("statAudibleTabs");

// Exibir Notificação Toast
let toastTimeout = null;
function showToast(msg) {
  if (toastTimeout) clearTimeout(toastTimeout);
  elToast.textContent = msg;
  elToast.classList.add("show");
  toastTimeout = setTimeout(() => {
    elToast.classList.remove("show");
  }, 2500);
}

// Formatar RAM (MB ou GB)
function formatMemory(mb) {
  if (!mb || mb <= 0) return "0 MB";
  if (mb >= 1024) {
    return `${(mb / 1024).toFixed(2)} GB`;
  }
  return `${mb} MB`;
}

// Renderizar UI com o estado atual
function renderUI() {
  const { stats, settings, activeHostname } = appState;

  // Cartão 1: RAM Poupada
  elRamSaved.textContent = formatMemory(stats.currentSavedMB);
  elRamDetail.textContent = stats.discardedTabs > 0 
    ? `${stats.discardedTabs} abas liberando memória` 
    : "Nenhuma aba suspensa no momento";

  // Cartão 2: Abas Suspensas / Total
  elDiscardedTabs.firstChild.textContent = stats.discardedTabs + " ";
  elTotalTabs.textContent = `/ ${stats.totalTabs}`;
  const pct = stats.totalTabs > 0 ? (stats.discardedTabs / stats.totalTabs) * 100 : 0;
  elProgressBar.style.width = `${Math.min(100, Math.round(pct))}%`;

  // Botão Fechar Repetidas com contagem em tempo real
  const dupCount = stats.duplicateCount || 0;
  if (closeDuplicatesText) {
    closeDuplicatesText.textContent = dupCount > 0 ? `Fechar Repetidas (${dupCount})` : "Fechar Repetidas";
  }
  btnCloseDuplicates.classList.toggle("has-duplicates", dupCount > 0);

  // Configurações - Inatividade
  const mins = settings.inactivityMinutes || 20;
  inactivityHint.textContent = mins < 60 ? `${mins} minutos` : `${mins / 60} hora`;
  document.querySelectorAll(".pill").forEach((pill) => {
    const pMin = parseInt(pill.dataset.minutes, 10);
    pill.classList.toggle("active", pMin === mins);
  });

  // Toggles
  toggleAutoDiscard.checked = !!settings.autoDiscardEnabled;
  toggleAutoCloseDuplicates.checked = !!settings.autoCloseDuplicates;
  toggleProtectAudible.checked = !!settings.protectAudible;
  toggleProtectPinned.checked = !!settings.protectPinned;
  toggleAutoCache.checked = !!settings.autoClearCache;

  // Whitelist: Site atual
  if (activeHostname && !["newtab", "extensions", ""].includes(activeHostname)) {
    quickProtectContainer.style.display = "block";
    const isAlreadyWhitelisted = settings.whitelist.includes(activeHostname);
    if (isAlreadyWhitelisted) {
      protectCurrentText.textContent = `✓ ${activeHostname} protegido`;
      btnProtectCurrentTab.disabled = true;
      btnProtectCurrentTab.style.opacity = "0.7";
    } else {
      protectCurrentText.textContent = `+ Proteger ${activeHostname}`;
      btnProtectCurrentTab.disabled = false;
      btnProtectCurrentTab.style.opacity = "1";
    }
  } else {
    quickProtectContainer.style.display = "none";
  }

  // Lista de tags da Whitelist
  whitelistTags.innerHTML = "";
  if (!settings.whitelist || settings.whitelist.length === 0) {
    whitelistTags.innerHTML = '<span style="font-size:11px;color:var(--text-muted);">Nenhum site adicionado.</span>';
  } else {
    settings.whitelist.forEach((domain) => {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.innerHTML = `<span>${domain}</span><span class="tag-remove" data-domain="${domain}">&times;</span>`;
      whitelistTags.appendChild(tag);
    });
  }

  // Estatísticas detalhadas
  statLifetimeDiscarded.textContent = stats.totalDiscardedLifetime.toLocaleString();
  statCacheCleans.textContent = stats.totalCacheCleans.toLocaleString();
  statAudibleTabs.textContent = stats.audibleTabs;

  if (stats.lastCacheCleanTimestamp) {
    const date = new Date(stats.lastCacheCleanTimestamp);
    statLastCacheClean.textContent = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } else {
    statLastCacheClean.textContent = "Nunca";
  }
}

// Buscar estado do Service Worker
async function loadState() {
  try {
    const response = await chrome.runtime.sendMessage({ action: "GET_STATE" });
    if (response && response.success) {
      appState = {
        settings: response.settings,
        stats: response.stats,
        activeHostname: response.activeHostname
      };
      renderUI();
    }
  } catch (err) {
    console.error("Falha ao carregar estado:", err);
  }
}

// Salvar configurações
async function updateSettings(partial) {
  appState.settings = { ...appState.settings, ...partial };
  try {
    await chrome.runtime.sendMessage({
      action: "UPDATE_SETTINGS",
      settings: appState.settings
    });
    renderUI();
  } catch (err) {
    console.error("Erro ao salvar configurações:", err);
  }
}

// Configuração dos Event Listeners
function setupEventListeners() {
  // Navegação de abas (Tabs)
  document.querySelectorAll(".tab-link").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-link").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const targetId = "tab" + btn.dataset.tab.charAt(0).toUpperCase() + btn.dataset.tab.slice(1);
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Atualizar
  btnRefresh.addEventListener("click", async () => {
    btnRefresh.style.transform = "rotate(180deg)";
    await loadState();
    setTimeout(() => (btnRefresh.style.transform = ""), 300);
    showToast("Dados atualizados!");
  });

  // Ação Rápida: Liberar Memória Agora
  btnDiscardNow.addEventListener("click", async () => {
    btnDiscardNow.disabled = true;
    btnDiscardNow.style.opacity = "0.7";
    try {
      const res = await chrome.runtime.sendMessage({ action: "DISCARD_ALL_NOW" });
      if (res && res.success) {
        showToast(res.count > 0 ? `⚡ ${res.count} abas suspensas!` : "Todas as abas já estão otimizadas!");
      }
      await loadState();
    } catch (err) {
      showToast("Erro ao suspender abas");
    } finally {
      btnDiscardNow.disabled = false;
      btnDiscardNow.style.opacity = "1";
    }
  });

  // Ação Rápida: Limpar Cache
  btnClearCache.addEventListener("click", async () => {
    btnClearCache.disabled = true;
    try {
      const res = await chrome.runtime.sendMessage({ action: "CLEAR_CACHE_NOW" });
      if (res && res.success) {
        showToast("🧹 Cache de rede limpo com sucesso!");
      } else {
        showToast("Erro ao limpar cache");
      }
      await loadState();
    } catch (err) {
      showToast("Erro ao executar limpeza");
    } finally {
      btnClearCache.disabled = false;
    }
  });

  // Ação Rápida: Fechar Duplicadas
  btnCloseDuplicates.addEventListener("click", async () => {
    btnCloseDuplicates.disabled = true;
    try {
      const res = await chrome.runtime.sendMessage({ action: "CLOSE_DUPLICATES_NOW" });
      if (res && res.success) {
        showToast(res.count > 0 ? `📑 ${res.count} abas duplicadas fechadas!` : "Nenhuma aba repetida encontrada.");
      }
      await loadState();
    } catch (err) {
      showToast("Erro ao fechar duplicadas");
    } finally {
      btnCloseDuplicates.disabled = false;
    }
  });

  // Pílulas de tempo
  timePresets.addEventListener("click", (e) => {
    const pill = e.target.closest(".pill");
    if (!pill) return;
    const minutes = parseInt(pill.dataset.minutes, 10);
    updateSettings({ inactivityMinutes: minutes });
    showToast(`Tempo de inatividade: ${minutes}m`);
  });

  // Toggles de configuração
  toggleAutoDiscard.addEventListener("change", (e) => {
    updateSettings({ autoDiscardEnabled: e.target.checked });
  });

  toggleAutoCloseDuplicates.addEventListener("change", (e) => {
    updateSettings({ autoCloseDuplicates: e.target.checked });
    if (e.target.checked) {
      showToast("Fechamento automático de duplicadas ativado!");
    }
  });

  toggleProtectAudible.addEventListener("change", (e) => {
    updateSettings({ protectAudible: e.target.checked });
  });

  toggleProtectPinned.addEventListener("change", (e) => {
    updateSettings({ protectPinned: e.target.checked });
  });

  toggleAutoCache.addEventListener("change", (e) => {
    updateSettings({ autoClearCache: e.target.checked });
  });

  // Whitelist: Proteger Site Atual
  btnProtectCurrentTab.addEventListener("click", () => {
    if (!appState.activeHostname) return;
    const currentList = appState.settings.whitelist || [];
    if (!currentList.includes(appState.activeHostname)) {
      updateSettings({ whitelist: [...currentList, appState.activeHostname] });
      showToast(`Site ${appState.activeHostname} protegido!`);
    }
  });

  // Whitelist: Formulário manual
  addDomainForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let val = domainInput.value.trim().toLowerCase();
    if (!val) return;

    // Remove protocolo http:// ou https:// e barras finais
    val = val.replace(/^https?:\/\//, "").replace(/\/.*$/, "");

    const currentList = appState.settings.whitelist || [];
    if (!currentList.includes(val)) {
      updateSettings({ whitelist: [...currentList, val] });
      domainInput.value = "";
      showToast(`Domínio ${val} adicionado!`);
    } else {
      showToast("Domínio já está na lista");
    }
  });

  // Whitelist: Remover Tag
  whitelistTags.addEventListener("click", (e) => {
    const removeBtn = e.target.closest(".tag-remove");
    if (!removeBtn) return;
    const domain = removeBtn.dataset.domain;
    const currentList = (appState.settings.whitelist || []).filter((d) => d !== domain);
    updateSettings({ whitelist: currentList });
    showToast(`Domínio ${domain} removido`);
  });
}

// Inicializar ao carregar o popup
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadState();
});
