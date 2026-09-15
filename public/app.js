// News Portal & Archive App — Vercel Deploy

let allEditions = [];
let recentRegionalEditions = [];
let historicalRegionalEditions = [];
let currentFilter = 'all';
let searchQuery = '';
let isHistoricalOpen = false;

// Elementos do DOM
const heroSection = document.getElementById('hero-featured');
const editionsGrid = document.getElementById('editions-grid');
const tabButtons = document.querySelectorAll('.tab-btn');
const searchInput = document.getElementById('search-input');
const modalOverlay = document.getElementById('modal-overlay');
const modalIframe = document.getElementById('modal-iframe');
const modalTitle = document.getElementById('modal-title');
const modalDate = document.getElementById('modal-date');
const modalExternalLink = document.getElementById('modal-external-link');
const btnCloseModal = document.getElementById('btn-close-modal');

// Elementos das Edições Históricas
const btnHistorical = document.getElementById('btn-historical');
const historicalContainer = document.getElementById('historical-container');
const historicalGrid = document.getElementById('historical-grid');
const historicalCount = document.getElementById('historical-count');
const historicalChevron = document.getElementById('historical-chevron');

// Formatação de data em português
function formatDatePT(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length !== 3) return dateStr;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  const d = new Date(year, month, day);
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
}

// Inicialização
async function init() {
  try {
    const res = await fetch('data/archive_index.json?v=' + Date.now());
    if (!res.ok) throw new Error('Não foi possível carregar o índice de edições');
    allEditions = await res.json();
    
    // Separa as edições regionais de Fatos da Região (Curitiba & PR)
    const regionalEditions = allEditions.filter(ed => ed.type === 'regional' || (!ed.type || (ed.type !== 'autismo' && ed.type !== 'brasil')));

    // O Hero principal mostra a edição mais recente de Fatos da Região
    const latestRegional = regionalEditions[0] || allEditions[0];
    renderHero(latestRegional);

    // Mantém em tela apenas as últimas 24 horas: a edição atual e mais 2 de histórico (ciclo de 3 turnos: 08h, 13h, 19h)
    recentRegionalEditions = regionalEditions.slice(0, 3);
    // As demais edições compõem o arquivo histórico acessível sob demanda
    historicalRegionalEditions = regionalEditions.slice(3);

    renderGrid();
    renderHistoricalGrid();
    setupEventListeners();
    setupBrasilButton();
    setupAutismoButton();
    setupHistoricalToggle();
    checkUrlParams();
  } catch (err) {
    console.error('Erro ao carregar dados:', err);
    editionsGrid.innerHTML = `
      <div class="empty-state">
        <span>⚠️</span>
        <h3>Nenhuma edição carregada</h3>
        <p>Verifique se o arquivo data/archive_index.json está acessível.</p>
      </div>
    `;
  }
}

// Configura o botão específico para abrir o relatório de Notícias Brasil & Mundo
function setupBrasilButton() {
  const btn = document.getElementById('btn-open-brasil');
  if (!btn) return;

  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const latestBrasil = allEditions.find(ed => ed.type === 'brasil' || ed.type === 'geral');
    if (latestBrasil) {
      openEditionModal(latestBrasil.id);
    } else {
      modalTitle.textContent = 'Notícias Brasil & Mundo — Edição Atual';
      modalDate.textContent = 'Boletim Nacional';
      modalExternalLink.href = 'data/editions/noticias_brasil_2026-09-14.html';
      modalIframe.src = 'data/editions/noticias_brasil_2026-09-14.html';
      modalOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  });
}

// Configura o botão específico para abrir o relatório de Notícias de Autismo
function setupAutismoButton() {
  const btn = document.getElementById('btn-open-autismo');
  if (!btn) return;

  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const latestAutismo = allEditions.find(ed => ed.type === 'autismo');
    if (latestAutismo) {
      openEditionModal(latestAutismo.id);
    } else {
      modalTitle.textContent = 'Notícias Autismo Brasil — Edição Diária (09h)';
      modalDate.textContent = 'Boletim Especial';
      modalExternalLink.href = 'data/editions/noticias_autismo_2026-09-14.html';
      modalIframe.src = 'data/editions/noticias_autismo_2026-09-14.html';
      modalOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  });
}

// Renderiza a edição mais recente no Hero
function renderHero(latest) {
  if (!latest) {
    heroSection.style.display = 'none';
    return;
  }
  heroSection.style.display = 'block';

  const badgeClass = 'type-regional';
  const badgeText = latest.type_label ? `${latest.type_label} — Mais Recente` : '🏙️ Fatos da Região — Mais Recente';
  const formattedDate = formatDatePT(latest.date);

  const sourcesHtml = (latest.sources || [])
    .map(s => `<span class="source-pill">${s}</span>`)
    .join('');

  heroSection.innerHTML = `
    <div class="featured-card">
      <div class="featured-top">
        <span class="featured-badge">${badgeText}</span>
        <span class="featured-date">📅 ${formattedDate} às ${latest.time}</span>
      </div>
      <h2>${latest.title}</h2>
      <p class="featured-summary">${latest.summary}</p>
      <div class="featured-footer">
        <div class="sources-pills">
          ${sourcesHtml}
        </div>
        <button class="btn-read-now" onclick="openEditionModal('${latest.id}')">
          📖 Ler Edição Completa
        </button>
      </div>
    </div>
  `;
}

// Cria o HTML padronizado para um card de edição
function createEditionCardHtml(ed) {
  const badgeClass = 'type-regional';
  const badgeText = ed.type_label || '🏙️ Fatos da Região';
  const formattedDate = formatDatePT(ed.date);

  return `
    <div class="edition-card">
      <div>
        <div class="card-meta">
          <span class="card-type-badge ${badgeClass}">${badgeText}</span>
          <span class="card-date">${formattedDate} • ${ed.time}</span>
        </div>
        <h3>${ed.title}</h3>
        <p class="card-summary">${ed.summary}</p>
      </div>
      <div class="card-footer">
        <div class="sources-pills" style="max-width: 68%;">
          ${(ed.sources || []).slice(0, 4).map(s => `<span class="source-pill" style="font-size: 0.7rem; padding: 2px 7px;">${s}</span>`).join('')}
          ${(ed.sources && ed.sources.length > 4) ? `<span class="source-pill" style="font-size: 0.7rem; padding: 2px 7px; color: var(--accent-cyan); border-color: rgba(56, 189, 248, 0.3);">+${ed.sources.length - 4}</span>` : ''}
        </div>
        <button class="btn-view-edition" onclick="openEditionModal('${ed.id}')">
          Abrir ➔
        </button>
      </div>
    </div>
  `;
}

// Filtra uma lista de edições de acordo com o turno e a busca
function filterEditionList(list) {
  return list.filter(ed => {
    // Filtro por turno
    if (currentFilter === 'tarde') {
      const isTarde = (ed.type_label || '').toLowerCase().includes('tarde') || (ed.time || '').startsWith('13:');
      if (!isTarde) return false;
    } else if (currentFilter === 'manha') {
      const isManha = (ed.type_label || '').toLowerCase().includes('manhã') || (ed.time || '').startsWith('08:') || (ed.time || '').startsWith('09:') || (ed.time || '').startsWith('10:');
      if (!isManha) return false;
    } else if (currentFilter === 'noite') {
      const isNoite = (ed.type_label || '').toLowerCase().includes('noite') || (ed.time || '').startsWith('19:');
      if (!isNoite) return false;
    }

    // Filtro de busca
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchTitle = (ed.title || '').toLowerCase().includes(q);
      const matchSummary = (ed.summary || '').toLowerCase().includes(q);
      const matchDate = (ed.date || '').toLowerCase().includes(q);
      const matchSources = (ed.sources || []).some(s => s.toLowerCase().includes(q));
      return matchTitle || matchSummary || matchDate || matchSources;
    }
    return true;
  });
}

// Renderiza o grid de edições recentes (últimas 24h)
function renderGrid() {
  const filtered = filterEditionList(recentRegionalEditions);

  if (filtered.length === 0) {
    editionsGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <span>🔍</span>
        <h3>Nenhuma edição recente encontrada</h3>
        <p>Tente alterar o filtro de categoria ou consulte as edições em "Edições Históricas" abaixo.</p>
      </div>
    `;
    return;
  }

  editionsGrid.innerHTML = filtered.map(createEditionCardHtml).join('');
}

// Renderiza o grid de edições históricas arquivadas
function renderHistoricalGrid() {
  if (!historicalGrid) return;
  const filtered = filterEditionList(historicalRegionalEditions);

  // Atualiza contador do badge
  if (historicalCount) {
    const total = historicalRegionalEditions.length;
    if (searchQuery || currentFilter !== 'all') {
      historicalCount.textContent = `${filtered.length} de ${total} encontradas`;
    } else {
      historicalCount.textContent = `${total} edições arquivadas`;
    }
  }

  if (filtered.length === 0) {
    historicalGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <span>📁</span>
        <h3>Nenhuma edição histórica encontrada</h3>
        <p>Não há edições no arquivo histórico correspondentes ao filtro atual.</p>
      </div>
    `;
    return;
  }

  historicalGrid.innerHTML = filtered.map(createEditionCardHtml).join('');
}

// Alterna a exibição da seção de Edições Históricas
function setupHistoricalToggle() {
  if (!btnHistorical || !historicalContainer) return;

  btnHistorical.addEventListener('click', () => {
    isHistoricalOpen = !isHistoricalOpen;
    updateHistoricalVisibility();
  });
}

function updateHistoricalVisibility() {
  if (!btnHistorical || !historicalContainer) return;

  if (isHistoricalOpen) {
    historicalContainer.style.display = 'block';
    btnHistorical.setAttribute('aria-expanded', 'true');
    btnHistorical.classList.add('active');
    if (historicalChevron) historicalChevron.textContent = '▴';
  } else {
    historicalContainer.style.display = 'none';
    btnHistorical.setAttribute('aria-expanded', 'false');
    btnHistorical.classList.remove('active');
    if (historicalChevron) historicalChevron.textContent = '▾';
  }
}

// Configura eventos de clique e input
function setupEventListeners() {
  // Tabs
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderGrid();
      renderHistoricalGrid();
    });
  });

  // Busca
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.trim();
    renderGrid();
    renderHistoricalGrid();

    // Se o usuário estiver pesquisando e houver resultados históricos, expande automaticamente
    if (searchQuery && filterEditionList(historicalRegionalEditions).length > 0 && !isHistoricalOpen) {
      isHistoricalOpen = true;
      updateHistoricalVisibility();
    }
  });

  // Fechar Modal
  btnCloseModal.addEventListener('click', closeEditionModal);
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeEditionModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
      closeEditionModal();
    }
  });
}

// Abrir Edição no Modal
function openEditionModal(editionId) {
  const edition = allEditions.find(e => e.id === editionId);
  if (!edition) return;

  modalTitle.textContent = edition.title;
  modalDate.textContent = `Publicado em ${formatDatePT(edition.date)} às ${edition.time}`;
  modalExternalLink.href = edition.file;
  modalIframe.src = edition.file;

  modalOverlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  // Atualiza hash da URL para permitir compartilhamento direto
  history.replaceState(null, '', `?edition=${editionId}`);
}

// Fechar Modal
function closeEditionModal() {
  modalOverlay.classList.remove('active');
  modalIframe.src = 'about:blank';
  document.body.style.overflow = '';
  history.replaceState(null, '', window.location.pathname);
}

// Checa parâmetros na URL para abrir direto uma edição
function checkUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const editionId = params.get('edition');
  if (editionId) {
    openEditionModal(editionId);
  }
}

// Dispara inicialização
document.addEventListener('DOMContentLoaded', init);
