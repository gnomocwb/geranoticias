/**
 * Gera Notícias — Extensão Chrome Oficial (Curitiba, RMC & Autismo)
 * Lógica reativa do popup (Manifest V3)
 */

const RAW_BASE_URL = "https://raw.githubusercontent.com/gnomocwb/geranoticias/main/public/";
const INDEX_URL = `${RAW_BASE_URL}data/archive_index.json`;

// Elementos da UI
const tabCuritiba = document.getElementById("tabCuritiba");
const tabAutismo = document.getElementById("tabAutismo");
const panelCuritiba = document.getElementById("panelCuritiba");
const panelAutismo = document.getElementById("panelAutismo");
const badgeCuritiba = document.getElementById("badgeCuritiba");
const badgeAutismo = document.getElementById("badgeAutismo");

const loadingState = document.getElementById("loadingState");
const errorState = document.getElementById("errorState");
const errorMessage = document.getElementById("errorMessage");
const btnRetry = document.getElementById("btnRetry");
const btnRefresh = document.getElementById("btnRefresh");
const lastUpdatedText = document.getElementById("lastUpdatedText");

const curitibaLatestContainer = document.getElementById("curitibaLatestContainer");
const curitibaHistoryContainer = document.getElementById("curitibaHistoryContainer");
const autismoLatestContainer = document.getElementById("autismoLatestContainer");
const autismoHistoryContainer = document.getElementById("autismoHistoryContainer");

// Modal do Leitor
const readerModal = document.getElementById("readerModal");
const readerTitle = document.getElementById("readerTitle");
const readerBadge = document.getElementById("readerBadge");
const readerBody = document.getElementById("readerBody");
const btnCloseReader = document.getElementById("btnCloseReader");

// Estado
let currentData = {
  regional: [],
  autismo: []
};

// Inicialização
document.addEventListener("DOMContentLoaded", async () => {
  initEventListeners();
  
  // Limpa o badge de novidades no ícone
  if (chrome?.runtime?.sendMessage) {
    chrome.runtime.sendMessage({ action: "clear_badge" }).catch(() => {});
  }

  // Restaura última aba ativa
  const stored = await chrome.storage.local.get(["active_tab", "cached_editions", "last_updated"]);
  if (stored.active_tab === "autismo") {
    switchTab("autismo");
  } else {
    switchTab("regional");
  }

  // Se houver cache prévio, renderiza imediatamente para 0ms de espera
  if (stored.cached_editions && Array.isArray(stored.cached_editions)) {
    processEditions(stored.cached_editions);
    renderAll();
    loadingState.style.display = "none";
    if (stored.last_updated) {
      updateTimeLabel(stored.last_updated);
    }
  }

  // Faz a sincronização em tempo real
  await fetchLatestNews();
});

function initEventListeners() {
  tabCuritiba.addEventListener("click", () => switchTab("regional"));
  tabAutismo.addEventListener("click", () => switchTab("autismo"));

  btnRefresh.addEventListener("click", async () => {
    const icon = btnRefresh.querySelector(".refresh-icon");
    if (icon) icon.classList.add("rotating");
    await fetchLatestNews(true);
    setTimeout(() => {
      if (icon) icon.classList.remove("rotating");
    }, 600);
  });

  btnRetry.addEventListener("click", () => fetchLatestNews(true));

  btnCloseReader.addEventListener("click", () => {
    readerModal.style.display = "none";
  });

  // Fechar leitor com ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && readerModal.style.display === "flex") {
      readerModal.style.display = "none";
    }
  });
}

function switchTab(tabKey) {
  if (tabKey === "regional") {
    tabCuritiba.classList.add("active");
    tabCuritiba.setAttribute("aria-selected", "true");
    tabAutismo.classList.remove("active");
    tabAutismo.setAttribute("aria-selected", "false");

    panelCuritiba.style.display = "block";
    panelAutismo.style.display = "none";
  } else {
    tabAutismo.classList.add("active");
    tabAutismo.setAttribute("aria-selected", "true");
    tabCuritiba.classList.remove("active");
    tabCuritiba.setAttribute("aria-selected", "false");

    panelAutismo.style.display = "block";
    panelCuritiba.style.display = "none";
  }

  chrome.storage.local.set({ active_tab: tabKey }).catch(() => {});
}

async function fetchLatestNews(forceLoading = false) {
  if (forceLoading && (!currentData.regional.length && !currentData.autismo.length)) {
    loadingState.style.display = "flex";
    errorState.style.display = "none";
  }

  try {
    const timestamp = Date.now();
    const response = await fetch(`${INDEX_URL}?t=${timestamp}`);
    if (!response.ok) {
      throw new Error(`Servidor retornou HTTP ${response.status}`);
    }

    const allEditions = await response.json();
    if (!Array.isArray(allEditions)) {
      throw new Error("Formato de dados inesperado.");
    }

    processEditions(allEditions);
    renderAll();

    loadingState.style.display = "none";
    errorState.style.display = "none";

    // Atualiza cache local
    const filtered = allEditions.filter(it => it.type === "regional" || it.type === "autismo");
    await chrome.storage.local.set({
      cached_editions: filtered,
      last_updated: timestamp
    });

    updateTimeLabel(timestamp);
  } catch (err) {
    console.error("[Gera Notícias Popup]", err);
    if (!currentData.regional.length && !currentData.autismo.length) {
      loadingState.style.display = "none";
      errorState.style.display = "flex";
      errorMessage.textContent = `Não foi possível atualizar agora (${err.message}).`;
    }
  }
}

function processEditions(editions) {
  currentData.regional = editions.filter(it => it.type === "regional");
  currentData.autismo = editions.filter(it => it.type === "autismo");
}

function renderAll() {
  renderPanel(
    currentData.regional,
    curitibaLatestContainer,
    curitibaHistoryContainer,
    "curitiba",
    "🏙️ Curitiba & RMC"
  );

  renderPanel(
    currentData.autismo,
    autismoLatestContainer,
    autismoHistoryContainer,
    "autismo",
    "🧩 Autismo Brasil"
  );
}

function renderPanel(list, latestEl, historyEl, themeClass, defaultTitle) {
  latestEl.innerHTML = "";
  historyEl.innerHTML = "";

  if (!list || list.length === 0) {
    latestEl.innerHTML = `
      <div class="edition-card-highlight ${themeClass}">
        <p class="edition-summary">Nenhuma edição disponível no momento.</p>
      </div>
    `;
    return;
  }

  const latest = list[0];
  const history = list.slice(1, 5);

  // Card Principal (Última Edição)
  const card = document.createElement("div");
  card.className = `edition-card-highlight ${themeClass}`;

  const formattedDate = formatDateString(latest.date, latest.time);

  // Parse do sumário para links clicáveis limpos
  const parsedSummary = parseMarkdownLinks(latest.summary || "Resumo analítico das notícias do período.");

  let sourcesHtml = "";
  if (latest.sources && Array.isArray(latest.sources)) {
    sourcesHtml = latest.sources.map(s => `<span class="source-chip">${escapeHtml(s)}</span>`).join("");
  }

  card.innerHTML = `
    <div class="card-top">
      <span class="badge-edition">${escapeHtml(latest.type_label || defaultTitle)}</span>
      <span class="edition-date">${formattedDate}</span>
    </div>
    <h2 class="edition-title">${escapeHtml(latest.title || defaultTitle)}</h2>
    <div class="edition-summary">${parsedSummary}</div>
    ${sourcesHtml ? `
      <div class="edition-sources">
        <span class="sources-label">Fontes:</span>
        ${sourcesHtml}
      </div>
    ` : ""}
    <div class="card-actions">
      <button class="btn-read-full" data-file="${escapeHtml(latest.file || '')}" data-title="${escapeHtml(latest.title)}" data-badge="${escapeHtml(latest.type_label)}">
        📖 Ler Edição Completa
      </button>
    </div>
  `;

  // Listener para botão de ler edição completa
  const btnRead = card.querySelector(".btn-read-full");
  if (btnRead) {
    btnRead.addEventListener("click", () => {
      openReader(latest.file, latest.title, latest.type_label);
    });
  }

  latestEl.appendChild(card);

  // Lista de Edições Anteriores
  if (history.length > 0) {
    history.forEach(item => {
      const itemEl = document.createElement("div");
      itemEl.className = "history-item";
      const hDate = formatDateString(item.date, item.time);

      itemEl.innerHTML = `
        <div class="history-info">
          <span class="history-title">${escapeHtml(item.type_label || item.title)}</span>
          <span class="history-meta">${hDate} • ${item.sources ? item.sources.length : 0} fontes</span>
        </div>
        <span class="history-arrow">›</span>
      `;

      itemEl.addEventListener("click", () => {
        openReader(item.file, item.title, item.type_label);
      });

      historyEl.appendChild(itemEl);
    });
  } else {
    historyEl.innerHTML = `<p style="font-size: 11px; color: var(--text-dim); padding: 6px 0;">Nenhuma edição anterior no arquivo.</p>`;
  }
}

async function openReader(filePath, title, badge) {
  if (!filePath) return;

  readerTitle.textContent = title || "Edição";
  readerBadge.textContent = badge || "Leitura";
  readerBody.innerHTML = `
    <div style="text-align: center; padding: 40px; color: var(--text-muted);">
      <div class="spinner" style="margin: 0 auto 10px;"></div>
      <p>Carregando edição completa...</p>
    </div>
  `;
  readerModal.style.display = "flex";

  try {
    const fullUrl = `${RAW_BASE_URL}${filePath}?t=${Date.now()}`;
    const resp = await fetch(fullUrl);
    if (!resp.ok) throw new Error("Não foi possível carregar a edição.");
    
    const htmlText = await resp.text();
    
    // Extrai o conteúdo do corpo ou container principal para exibição limpa
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, "text/html");
    const container = doc.querySelector(".container") || doc.querySelector("main") || doc.body;

    // Garante que todos os links abram em nova aba
    container.querySelectorAll("a").forEach(a => {
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener noreferrer");
    });

    readerBody.innerHTML = container.innerHTML;
  } catch (err) {
    readerBody.innerHTML = `
      <div style="text-align: center; padding: 30px; color: #ff7b72;">
        <p>⚠️ Falha ao carregar a edição: ${escapeHtml(err.message)}</p>
        <p style="margin-top: 10px;">
          <a href="https://github.com/gnomocwb/geranoticias" target="_blank" style="color: var(--accent-curitiba);">Abrir portal no GitHub</a>
        </p>
      </div>
    `;
  }
}

function formatDateString(dateStr, timeStr) {
  if (!dateStr) return "Recente";
  try {
    const parts = dateStr.split("-");
    const formattedDate = `${parts[2]}/${parts[1]}`;
    return timeStr ? `${formattedDate} às ${timeStr}` : formattedDate;
  } catch {
    return dateStr;
  }
}

function updateTimeLabel(timestamp) {
  const date = new Date(timestamp);
  const time = date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  lastUpdatedText.textContent = `Sincronizado às ${time}`;
}

function parseMarkdownLinks(text) {
  if (!text) return "";
  // Converte [texto](url) em <a href="url" target="_blank">texto</a>
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let sanitized = escapeHtml(text);
  sanitized = sanitized.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (match, title, url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-curitiba); font-weight: 600; text-decoration: none;">${title}</a>`;
  });
  return sanitized;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
