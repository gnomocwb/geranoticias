// News Portal & Archive App — Vercel Deploy

let allEditions = [];
let currentFilter = 'all';
let searchQuery = '';

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
    
    renderHero(allEditions[0]);
    renderGrid();
    setupEventListeners();
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

// Renderiza o grid de edições arquivadas
function renderGrid() {
  const filtered = allEditions.filter(ed => {
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

  if (filtered.length === 0) {
    editionsGrid.innerHTML = `
      <div class="empty-state">
        <span>🔍</span>
        <h3>Nenhuma edição encontrada</h3>
        <p>Tente alterar o filtro de categoria ou os termos da busca.</p>
      </div>
    `;
    return;
  }

  editionsGrid.innerHTML = filtered.map(ed => {
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
          <div class="sources-pills" style="max-width: 65%;">
            ${(ed.sources || []).slice(0, 3).map(s => `<span class="source-pill" style="font-size: 0.7rem; padding: 2px 7px;">${s}</span>`).join('')}
          </div>
          <button class="btn-view-edition" onclick="openEditionModal('${ed.id}')">
            Abrir ➔
          </button>
        </div>
      </div>
    `;
  }).join('');
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
    });
  });

  // Busca
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.trim();
    renderGrid();
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
