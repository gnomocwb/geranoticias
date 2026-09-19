// Background Service Worker para Gera Notícias (Manifest V3)

const DATA_URL = "https://raw.githubusercontent.com/gnomocwb/geranoticias/main/public/data/archive_index.json";
const ALARM_NAME = "check_geranoticias_editions";

// Configura o alarme ao instalar ou iniciar
chrome.runtime.onInstalled.addListener(() => {
  console.log("[Gera Notícias] Extensão instalada. Configurando verificação periódica...");
  chrome.alarms.create(ALARM_NAME, {
    periodInMinutes: 30
  });
  checkLatestEditions();
});

chrome.runtime.onStartup.addListener(() => {
  checkLatestEditions();
});

// Listener para o alarme
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAME) {
    checkLatestEditions();
  }
});

// Listener para mensagens vindas do popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "clear_badge") {
    chrome.action.setBadgeText({ text: "" });
    sendResponse({ status: "badge_cleared" });
  } else if (message.action === "force_refresh") {
    checkLatestEditions().then((res) => sendResponse(res));
    return true; // Resposta assíncrona
  }
});

async function checkLatestEditions() {
  try {
    const urlWithCacheBust = `${DATA_URL}?t=${Date.now()}`;
    const response = await fetch(urlWithCacheBust);
    if (!response.ok) {
      console.warn("[Gera Notícias] Falha ao consultar feed:", response.status);
      return { success: false, status: response.status };
    }

    const allEditions = await response.json();
    if (!Array.isArray(allEditions)) return { success: false };

    // Filtra exclusivamente Curitiba/RMC (regional) e Autismo (autismo)
    const filtered = allEditions.filter(item => item.type === "regional" || item.type === "autismo");

    const storage = await chrome.storage.local.get(["last_seen_id", "cached_editions"]);
    const lastSeenId = storage.last_seen_id;

    if (filtered.length > 0) {
      const latestEdition = filtered[0];

      // Atualiza o cache local para abertura instantânea do popup
      await chrome.storage.local.set({
        cached_editions: filtered,
        last_updated: Date.now()
      });

      // Se houver uma nova edição que o usuário ainda não viu, exibe o Badge
      if (lastSeenId && latestEdition.id !== lastSeenId) {
        chrome.action.setBadgeText({ text: "NOVO" });
        chrome.action.setBadgeBackgroundColor({ color: "#2563eb" });
      }
    }

    return { success: true, count: filtered.length };
  } catch (err) {
    console.warn("[Gera Notícias] Erro ao sincronizar em background:", err);
    return { success: false, error: err.message };
  }
}
