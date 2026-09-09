import re
import html
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
import feedparser
import urllib.request

logger = logging.getLogger("news_briefing.fetcher")

# Mapeamento de meses em português para parsing de datas
PT_MONTHS = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NewsBriefing/1.0"
)


@dataclass
class NewsItem:
    title: str
    link: str
    summary: str
    source_id: str
    source_name: str
    category: str
    published_at: Optional[datetime]
    language: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "category": self.category,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "language": self.language
        }


def clean_html_text(text: Optional[str]) -> str:
    """Remove tags HTML e caracteres indesejados de descrições e títulos."""
    if not text:
        return ""
    # Desfaz entidades HTML (ex: &amp;, &quot;, &#39;)
    decoded = html.unescape(text)
    # Remove tags HTML <...>
    clean = re.sub(r"<[^>]+>", " ", decoded)
    # Remove quebras extras e múltiplos espaços
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_date_flexible(date_str: Optional[str]) -> Optional[datetime]:
    """Parse flexível para datas em formatos RFC-822, ISO ou strings em português."""
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()

    # 1. Tentar parser padrão RFC-822 / email
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass

    # 2. Tentar ISO-8601
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass

    # 3. Formato comum em português (UOL): 'Qua, 09 Set 2026 19:02:28 -0300'
    match = re.search(
        r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})(?:\s+([+-]\d{4}))?",
        date_str,
    )
    if match:
        day, mon_str, year, hr, mn, sc, tz_str = match.groups()
        mon = PT_MONTHS.get(mon_str.lower())
        if mon:
            tz = timezone.utc
            if tz_str:
                tz_sign = 1 if tz_str[0] == "+" else -1
                tz_hrs = int(tz_str[1:3])
                tz_mins = int(tz_str[3:5])
                tz = timezone(tz_sign * timedelta(hours=tz_hrs, minutes=tz_mins))
            return datetime(int(year), mon, int(day), int(hr), int(mn), int(sc), tzinfo=tz)

    return None


def fetch_single_feed(feed_config: Dict[str, Any], timeout: int = 12) -> List[NewsItem]:
    """Baixa e processa um único feed RSS."""
    feed_id = feed_config.get("id", "desconhecido")
    feed_name = feed_config.get("name", feed_id)
    url = feed_config["url"]
    category = feed_config.get("category", "Geral")
    language = feed_config.get("language", "pt")

    items: List[NewsItem] = []
    try:
        # Usamos urllib com User-Agent para garantir que servidores exigentes aceitem a requisição
        req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()

        parsed = feedparser.parse(content)
        for entry in parsed.entries:
            title = clean_html_text(getattr(entry, "title", ""))
            if not title:
                continue

            link = getattr(entry, "link", "")
            raw_summary = (
                getattr(entry, "summary", "")
                or getattr(entry, "description", "")
            )
            summary = clean_html_text(raw_summary)

            # Tenta obter a data
            published_at = None
            date_raw = getattr(entry, "published", None) or getattr(entry, "pubDate", None) or getattr(entry, "updated", None)
            if date_raw:
                published_at = parse_date_flexible(date_raw)

            # Fallback para published_parsed se feedparser conseguiu
            if not published_at and getattr(entry, "published_parsed", None):
                try:
                    tt = entry.published_parsed
                    published_at = datetime(tt.tm_year, tt.tm_mon, tt.tm_mday, tt.tm_hour, tt.tm_min, tt.tm_sec, tzinfo=timezone.utc)
                except Exception:
                    pass

            items.append(
                NewsItem(
                    title=title,
                    link=link,
                    summary=summary,
                    source_id=feed_id,
                    source_name=feed_name,
                    category=category,
                    published_at=published_at,
                    language=language,
                )
            )
    except Exception as e:
        logger.warning(f"Erro ao obter feed '{feed_name}' ({url}): {e}")

    return items


def fetch_all_feeds(feeds: List[Dict[str, Any]], max_workers: int = 6, timeout: int = 12) -> List[NewsItem]:
    """Coleta notícias de todos os feeds simultaneamente usando threads."""
    all_items: List[NewsItem] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_feed = {
            executor.submit(fetch_single_feed, feed, timeout): feed
            for feed in feeds
        }
        for future in as_completed(future_to_feed):
            feed_cfg = future_to_feed[future]
            try:
                items = future.result()
                all_items.extend(items)
            except Exception as e:
                logger.error(f"Falha inesperada no worker do feed {feed_cfg.get('name')}: {e}")

    return all_items
