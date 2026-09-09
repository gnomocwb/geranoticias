/**
 * Chrome RAM Saver & Auto Tab Discarder
 * Background Service Worker (Manifest V3)
 */

// Chaves de armazenamento e configurações padrão
const DEFAULT_SETTINGS = {
  inactivityMinutes: 20,
  autoDiscardEnabled: true,
  protectAudible: true,
  protectPinned: true,
  autoClearCache: false,
  autoCloseDuplicates: false,
  cacheIntervalHours: 24,
  whitelist: [
    "meet.google.com",
    "zoom.us",
    "teams.microsoft.com",
    "music.youtube.com",
    "open.spotify.com"
  ],
  stats: {
    totalDiscarded: 0,
    totalCacheCleans: 0,
    estimatedRamSavedMB: 0
  }
};

const STORAGE = chrome.storage.session || chrome.storage.local;

// Helper: obter configurações atuais
async function getSettings() {
  const data = await chrome.storage.local.get("settings");
  return { ...DEFAULT_SETTINGS, ...(data.settings || {}) };
}

// Helper: salvar configurações
async function saveSettings(newSettings) {
  await chrome.storage.local.set({ settings: newSettings });
}

// Helper: obter mapa de atividade de abas
async function getTabActivityMap() {
  const data = await STORAGE.get("tabActivity");
  return data.tabActivity || {};
}

// Helper: atualizar última atividade de uma aba
async function markTabActive(tabId) {
  if (!tabId || tabId < 0) return;
  const activity = await getTabActivityMap();
  activity[tabId] = Date.now();
  await STORAGE.set({ tabActivity: activity });
}

// Helper: remover aba fechada do mapa
async function removeTabActivity(tabId) {
  const activity = await getTabActivityMap();
  if (activity[tabId]) {
    delete activity[tabId];
    await STORAGE.set({ tabActivity: activity });
  }
}

// Inicialização na instalação/atualização da extensão
chrome.runtime.onInstalled.addListener(async () => {
  const current = await chrome.storage.local.get("settings");
  if (!current.settings) {
    await saveSettings(DEFAULT_SETTINGS);
  }

  // Registra alarme periódico de checagem (1 minuto)
  await chrome.alarms.create("checkIdleTabsAlarm", { periodInMinutes: 1 });
  // Registra alarme de limpeza de cache automático (a cada hora para checar intervalo)
  await chrome.alarms.create("checkCacheAlarm", { periodInMinutes: 60 });

  // Inicializa mapa de atividade com as abas atuais
  const tabs = await chrome.tabs.query({});
  const activity = {};
  const now = Date.now();
  for (const tab of tabs) {
    activity[tab.id] = now;
  }
  await STORAGE.set({ tabActivity: activity });

  await updateBadge();
  console.log("Chrome RAM Saver instalado e alarmes configurados.");
});

// Listener de alarmes
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "checkIdleTabsAlarm") {
    await discardEligibleIdleTabs();
    const settings = await getSettings();
    if (settings.autoCloseDuplicates) {
      await closeDuplicateTabs();
    }
  } else if (alarm.name === "checkCacheAlarm") {
    await checkAutoCacheCleanup();
  }
});

// Rastreamento de foco e ativação de abas
chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  await markTabActive(tabId);
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (tab.active || changeInfo.status === "complete") {
    await markTabActive(tabId);
  }
  if (changeInfo.status === "complete") {
    const settings = await getSettings();
    if (settings.autoCloseDuplicates) {
      await closeDuplicateTabs();
    }
  }
  await updateBadge();
});

chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) return;
  try {
    const [tab] = await chrome.tabs.query({ active: true, windowId });
    if (tab?.id) {
      await markTabActive(tab.id);
    }
  } catch (e) {
    // Ignora eventuais janelas de devtools ou fechadas
  }
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  await removeTabActivity(tabId);
  await updateBadge();
});

// Verifica se uma aba pode ser descartada com base nas configurações e regras de proteção
function canDiscardTab(tab, settings, whitelist) {
  // Nunca descartar a aba ativa da janela
  if (tab.active) return false;

  // Se já estiver descartada, nada a fazer
  if (tab.discarded) return false;

  // Proteger se estiver reproduzindo áudio
  if (settings.protectAudible && tab.audible) return false;

  // Proteger se for fixada
  if (settings.protectPinned && tab.pinned) return false;

  // Proteger páginas internas do navegador ou sem URL válida
  if (!tab.url || 
      tab.url.startsWith("chrome://") || 
      tab.url.startsWith("chrome-extension://") || 
      tab.url.startsWith("edge://") ||
      tab.url.startsWith("about:") ||
      tab.url.startsWith("view-source:")) {
    return false;
  }

  // Checar Whitelist de domínios
  try {
    const urlObj = new URL(tab.url);
    const hostname = urlObj.hostname.toLowerCase();
    const isWhitelisted = whitelist.some((domain) => {
      const clean = domain.trim().toLowerCase();
      return clean && (hostname === clean || hostname.endsWith("." + clean));
    });
    if (isWhitelisted) return false;
  } catch (e) {
    return false;
  }

  return true;
}

// Descarte automático periódico de abas inativas
async function discardEligibleIdleTabs() {
  const settings = await getSettings();
  if (!settings.autoDiscardEnabled) return;

  const thresholdMs = (settings.inactivityMinutes || 20) * 60 * 1000;
  const activity = await getTabActivityMap();
  const tabs = await chrome.tabs.query({});
  const now = Date.now();
  let newlyDiscarded = 0;

  for (const tab of tabs) {
    if (!canDiscardTab(tab, settings, settings.whitelist)) continue;

    const lastActive = activity[tab.id] || now;
    const idleDuration = now - lastActive;

    if (idleDuration >= thresholdMs) {
      try {
        await chrome.tabs.discard(tab.id);
        newlyDiscarded++;
        console.log(`Aba ${tab.id} (${tab.title}) suspensa por inatividade.`);
      } catch (err) {
        console.warn(`Falha ao suspender aba ${tab.id}:`, err);
      }
    }
  }

  if (newlyDiscarded > 0) {
    settings.stats.totalDiscarded = (settings.stats.totalDiscarded || 0) + newlyDiscarded;
    settings.stats.estimatedRamSavedMB = (settings.stats.estimatedRamSavedMB || 0) + (newlyDiscarded * 120);
    await saveSettings(settings);
  }

  await updateBadge();
}

// Descarte manual forçado de todas as abas inativas elegíveis
async function discardAllInactiveNow() {
  const settings = await getSettings();
  const tabs = await chrome.tabs.query({});
  let discardedCount = 0;

  for (const tab of tabs) {
    if (!canDiscardTab(tab, settings, settings.whitelist)) continue;

    try {
      await chrome.tabs.discard(tab.id);
      discardedCount++;
    } catch (err) {
      console.warn(`Falha ao descartar aba ${tab.id}:`, err);
    }
  }

  if (discardedCount > 0) {
    settings.stats.totalDiscarded = (settings.stats.totalDiscarded || 0) + discardedCount;
    settings.stats.estimatedRamSavedMB = (settings.stats.estimatedRamSavedMB || 0) + (discardedCount * 120);
    await saveSettings(settings);
  }

  await updateBadge();
  return discardedCount;
}

// Normalizador robusto de URLs para detecção precisa de duplicatas
function normalizeTabUrl(tab) {
  const rawUrl = tab.url || tab.pendingUrl || "";
  if (!rawUrl) return null;

  // Ignorar páginas de sistema, extensões e páginas em branco
  if (
    rawUrl.startsWith("chrome://") ||
    rawUrl.startsWith("chrome-extension://") ||
    rawUrl.startsWith("edge://") ||
    rawUrl.startsWith("about:") ||
    rawUrl.startsWith("view-source:")
  ) {
    return null;
  }

  try {
    const u = new URL(rawUrl);
    const hostname = u.hostname.toLowerCase();
    
    // Normaliza pathname: remove barra final redundante
    let pathname = u.pathname;
    if (pathname.length > 1 && pathname.endsWith("/")) {
      pathname = pathname.slice(0, -1);
    }

    // Ordena parâmetros de busca para comparar ?a=1&b=2 com ?b=2&a=1
    const searchParams = new URLSearchParams(u.search);
    searchParams.sort();
    const search = searchParams.toString() ? "?" + searchParams.toString() : "";

    // Ignora o hash/âncora (#secao) para tratar como a mesma página
    return `${u.protocol}//${hostname}${u.port ? ":" + u.port : ""}${pathname}${search}`;
  } catch {
    return rawUrl.trim();
  }
}

// Contabilizar quantas abas duplicadas existem no momento
function countDuplicateTabsSync(tabs) {
  const urlGroups = new Map();
  let duplicates = 0;
  for (const tab of tabs) {
    const normUrl = normalizeTabUrl(tab);
    if (!normUrl) continue;
    const current = (urlGroups.get(normUrl) || 0) + 1;
    urlGroups.set(normUrl, current);
    if (current > 1) {
      duplicates++;
    }
  }
  return duplicates;
}

// Fechar abas duplicadas de forma inteligente e segura
async function closeDuplicateTabs() {
  const tabs = await chrome.tabs.query({});
  let focusedWindowId = null;
  try {
    const lastFocused = await chrome.windows.getLastFocused();
    focusedWindowId = lastFocused?.id;
  } catch (e) {}

  // Agrupa todas as abas por URL normalizada
  const urlGroups = new Map();

  for (const tab of tabs) {
    const normUrl = normalizeTabUrl(tab);
    if (!normUrl) continue;

    if (!urlGroups.has(normUrl)) {
      urlGroups.set(normUrl, []);
    }
    urlGroups.get(normUrl).push(tab);
  }

  const duplicatesToRemove = [];

  for (const [url, group] of urlGroups.entries()) {
    if (group.length <= 1) continue;

    // Ordena o grupo para definir qual aba MANTER aberta (índice 0):
    // 1. Aba ativa na janela focada atual
    // 2. Aba ativa em qualquer janela
    // 3. Aba reproduzindo som/áudio
    // 4. Aba fixada (pinned)
    // 5. Aba não descartada (já carregada na RAM)
    // 6. ID mais recente
    group.sort((a, b) => {
      const aIsFocusedActive = a.active && a.windowId === focusedWindowId;
      const bIsFocusedActive = b.active && b.windowId === focusedWindowId;
      if (aIsFocusedActive !== bIsFocusedActive) return bIsFocusedActive ? 1 : -1;

      if (a.active !== b.active) return b.active ? 1 : -1;
      if (a.audible !== b.audible) return b.audible ? 1 : -1;
      if (a.pinned !== b.pinned) return b.pinned ? 1 : -1;
      if (a.discarded !== b.discarded) return a.discarded ? 1 : -1;
      return b.id - a.id;
    });

    // Mantém o índice 0. Todos os demais do grupo (1 em diante) serão fechados
    for (let i = 1; i < group.length; i++) {
      duplicatesToRemove.push(group[i].id);
    }
  }

  let closedCount = 0;
  for (const tabId of duplicatesToRemove) {
    try {
      await chrome.tabs.remove(tabId);
      closedCount++;
    } catch (err) {
      console.warn(`Aviso ao fechar aba duplicada ${tabId}:`, err);
    }
  }

  await updateBadge();
  return closedCount;
}

// Limpeza de cache de rede do navegador
async function clearBrowserCache() {
  try {
    await chrome.browsingData.removeCache({ since: 0 });
    // Limpa também o cacheStorage de service workers
    await chrome.browsingData.remove({ since: 0 }, { cacheStorage: true });

    const settings = await getSettings();
    settings.stats.totalCacheCleans = (settings.stats.totalCacheCleans || 0) + 1;
    settings.stats.lastCacheCleanTimestamp = Date.now();
    await saveSettings(settings);

    return { success: true };
  } catch (err) {
    console.error("Erro ao limpar cache:", err);
    return { success: false, error: err.message };
  }
}

// Verificação de limpeza automática de cache
async function checkAutoCacheCleanup() {
  const settings = await getSettings();
  if (!settings.autoClearCache) return;

  const intervalMs = (settings.cacheIntervalHours || 24) * 60 * 60 * 1000;
  const lastClean = settings.stats.lastCacheCleanTimestamp || 0;
  const now = Date.now();

  if (now - lastClean >= intervalMs) {
    await clearBrowserCache();
    console.log("Limpeza automática de cache executada com sucesso.");
  }
}

// Atualizar o badge do ícone da extensão
async function updateBadge() {
  try {
    const tabs = await chrome.tabs.query({});
    const discardedTabs = tabs.filter((t) => t.discarded).length;

    if (discardedTabs > 0) {
      await chrome.action.setBadgeText({ text: String(discardedTabs) });
      await chrome.action.setBadgeBackgroundColor({ color: "#0072FF" });
    } else {
      await chrome.action.setBadgeText({ text: "" });
    }
  } catch (err) {
    // Ignora se contexto não estiver disponível
  }
}

// Comunicação com o popup (Mensageria)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message.action === "GET_STATE") {
        const settings = await getSettings();
        const tabs = await chrome.tabs.query({});
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });

        const totalTabs = tabs.length;
        const discardedTabs = tabs.filter((t) => t.discarded).length;
        const audibleTabs = tabs.filter((t) => t.audible).length;
        const activeTabs = totalTabs - discardedTabs;
        const duplicateCount = countDuplicateTabsSync(tabs);

        // Estima economia: ~120MB por aba descartada no momento + histórico acumulado
        const currentSavedMB = discardedTabs * 120;

        let activeHostname = "";
        if (activeTab?.url) {
          try {
            activeHostname = new URL(activeTab.url).hostname;
          } catch {}
        }

        sendResponse({
          success: true,
          stats: {
            totalTabs,
            discardedTabs,
            activeTabs,
            audibleTabs,
            duplicateCount,
            currentSavedMB,
            totalDiscardedLifetime: settings.stats.totalDiscarded || 0,
            totalCacheCleans: settings.stats.totalCacheCleans || 0,
            lastCacheCleanTimestamp: settings.stats.lastCacheCleanTimestamp || null
          },
          settings,
          activeHostname
        });
      } else if (message.action === "DISCARD_ALL_NOW") {
        const count = await discardAllInactiveNow();
        sendResponse({ success: true, count });
      } else if (message.action === "CLEAR_CACHE_NOW") {
        const result = await clearBrowserCache();
        sendResponse(result);
      } else if (message.action === "CLOSE_DUPLICATES_NOW") {
        const count = await closeDuplicateTabs();
        sendResponse({ success: true, count });
      } else if (message.action === "UPDATE_SETTINGS") {
        await saveSettings(message.settings);
        await updateBadge();
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: "Ação desconhecida" });
      }
    } catch (err) {
      console.error("Erro ao processar mensagem:", err);
      sendResponse({ success: false, error: err.message });
    }
  })();

  return true; // Mantém o canal de resposta aberto para operações assíncronas
});
