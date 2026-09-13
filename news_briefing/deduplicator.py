import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Set
from .fetcher import NewsItem

STOPWORDS = {
    # Português
    "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "sob", "sobre",
    "e", "ou", "mas", "que", "se", "nao", "não", "como", "foi", "sao", "são", "esta", "está",
    "diz", "apos", "após", "tem", "ter", "ao", "aos", "pela", "pelas", "pelo", "pelos",
    # Inglês
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "of", "from", "up", "about", "into", "over", "after", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "says", "said", "new"
}


def normalize_title(title: str) -> Set[str]:
    """Extrai radicais (stems) de palavras-chave normalizadas de um título para comparação."""
    clean = re.sub(r"[^\w\s]", " ", title.lower())
    stems = set()
    for w in clean.split():
        if len(w) > 2 and w not in STOPWORDS:
            # Redução simples de sufixo (prefix stem de 4 caracteres para lidar com variações verbais/plurais)
            stem = w[:4] if len(w) > 4 else w
            stems.add(stem)
    return stems


def token_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calcula a similaridade ponderada entre dois conjuntos de tokens/radicais."""
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    jaccard = len(intersection) / len(union) if union else 0.0
    
    # Se compartilharem 3 ou mais radicais significativos, considera alta relevância
    if len(intersection) >= 3:
        return max(jaccard, 0.4)
    if len(intersection) >= 2 and len(union) <= 10:
        return max(jaccard, 0.35)
    return jaccard


class ClusteredStory:
    def __init__(self, primary_item: NewsItem):
        self.primary_title = primary_item.title
        self.category = primary_item.category
        self.items: List[NewsItem] = [primary_item]
        self.sources: Set[str] = {primary_item.source_name}
        self.tokens: Set[str] = normalize_title(primary_item.title)
        self.latest_time = primary_item.published_at

    def add_item(self, item: NewsItem):
        self.items.append(item)
        self.sources.add(item.source_name)
        if item.published_at:
            if not self.latest_time or item.published_at > self.latest_time:
                self.latest_time = item.published_at
        # Atualiza conjunto de tokens combinados
        self.tokens.update(normalize_title(item.title))

    @property
    def links(self) -> List[Dict[str, str]]:
        return [{"source": it.source_name, "url": it.link, "title": it.title} for it in self.items]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.primary_title,
            "category": self.category,
            "sources": sorted(list(self.sources)),
            "links": self.links,
            "published_at": self.latest_time.isoformat() if self.latest_time else None,
            "summaries": [it.summary for it in self.items if it.summary],
            "items_count": len(self.items)
        }


def filter_by_time(items: List[NewsItem], hours: int = 14) -> List[NewsItem]:
    """Filtra itens publicados dentro da janela de tempo informada em horas."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)

    filtered = []
    undated = []

    for item in items:
        if item.published_at:
            # Converte para UTC se tiver timezone diferente
            pub_utc = item.published_at.astimezone(timezone.utc)
            if pub_utc >= cutoff:
                filtered.append(item)
        else:
            undated.append(item)

    # Se um feed não fornecer datas (ex: CNN edition sem pubDate), mantemos no máximo 5 itens do topo
    feed_counts: Dict[str, int] = {}
    for item in undated:
        count = feed_counts.get(item.source_id, 0)
        if count < 5:
            filtered.append(item)
            feed_counts[item.source_id] = count + 1

    return filtered


def cluster_and_deduplicate(items: List[NewsItem], similarity_threshold: float = 0.45) -> List[ClusteredStory]:
    """Agrupa notícias similares de diferentes veículos em uma única história consolidada."""
    clusters: List[ClusteredStory] = []

    for item in items:
        item_tokens = normalize_title(item.title)
        matched_cluster = None

        for cluster in clusters:
            sim = token_similarity(item_tokens, cluster.tokens)
            if sim >= similarity_threshold:
                matched_cluster = cluster
                break

        if matched_cluster:
            matched_cluster.add_item(item)
        else:
            clusters.append(ClusteredStory(item))

    # Ordena as histórias: mais citadas/fontes primeiro, depois por data mais recente
    clusters.sort(
        key=lambda c: (
            len(c.sources),
            c.latest_time.timestamp() if c.latest_time else 0
        ),
        reverse=True
    )

    return clusters
