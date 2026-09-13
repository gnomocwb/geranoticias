import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from news_briefing.fetcher import (
    clean_html_text,
    parse_date_flexible,
    NewsItem
)
from news_briefing.deduplicator import (
    normalize_title,
    token_similarity,
    cluster_and_deduplicate,
    filter_by_time
)
from news_briefing.formatters import convert_markdown_to_html
from news_briefing.config import load_configured_feeds


class TestNewsBriefing(unittest.TestCase):

    def test_feeds_json_loads(self):
        """Verifica se os feeds cadastrados são válidos e contêm URLs."""
        feeds = load_configured_feeds()
        self.assertGreater(len(feeds), 0)
        for feed in feeds:
            self.assertIn("id", feed)
            self.assertIn("url", feed)
            self.assertTrue(feed["url"].startswith("http"))

    def test_regional_feeds_json_loads(self):
        """Verifica se os feeds regionais (Curitiba e interior do Paraná) são válidos."""
        reg_path = Path(__file__).resolve().parent.parent / "news_briefing" / "feeds_regional.json"
        feeds = load_configured_feeds(custom_file=reg_path)
        self.assertGreater(len(feeds), 0)
        feed_ids = [f["id"] for f in feeds]
        self.assertIn("gazetadopovo_direct", feed_ids)
        self.assertIn("omaringa_direct", feed_ids)
        self.assertIn("folhadelondrina_direct", feed_ids)
        self.assertIn("diariodefoz_direct", feed_ids)
        self.assertIn("redesulnoticias_direct", feed_ids)

        gazeta = next(f for f in feeds if f["id"] == "gazetadopovo_direct")
        self.assertEqual(gazeta["url"], "https://www.gazetadopovo.com.br/rss/")
        self.assertEqual(gazeta["name"], "Gazeta do Povo")

        maringa = next(f for f in feeds if f["id"] == "omaringa_direct")
        self.assertEqual(maringa["url"], "https://omaringa.com.br/feed/")

        folha = next(f for f in feeds if f["id"] == "folhadelondrina_direct")
        self.assertEqual(folha["url"], "https://www.folhadelondrina.com.br/rss")

        foz = next(f for f in feeds if f["id"] == "diariodefoz_direct")
        self.assertEqual(foz["url"], "https://diariodefoz.com/feed/")

        rsn = next(f for f in feeds if f["id"] == "redesulnoticias_direct")
        self.assertEqual(rsn["url"], "https://redesuldenoticias.com.br/feed/")

    def test_clean_html_text(self):
        """Testa remoção de tags HTML e entidades."""
        raw = "<p>Texto com <b>negrito</b> e &amp; entidade.</p>"
        cleaned = clean_html_text(raw)
        self.assertEqual(cleaned, "Texto com negrito e & entidade.")

    def test_parse_date_flexible(self):
        """Testa parsing de datas em RFC, ISO e formato português."""
        # RFC-822
        d1 = parse_date_flexible("Wed, 09 Sep 2026 20:46:33 GMT")
        self.assertIsNotNone(d1)
        self.assertEqual(d1.year, 2026)
        self.assertEqual(d1.month, 9)

        # Português (UOL)
        d2 = parse_date_flexible("Qua, 09 Set 2026 19:02:28 -0300")
        self.assertIsNotNone(d2)
        self.assertEqual(d2.year, 2026)
        self.assertEqual(d2.month, 9)
        self.assertEqual(d2.day, 9)

        # None / Inválido
        self.assertIsNone(parse_date_flexible(None))
        self.assertIsNone(parse_date_flexible("data invalida"))

    def test_token_similarity_and_dedup(self):
        """Verifica similaridade e agrupamento de manchetes similares."""
        t1 = "Banco Central eleva taxa Selic para 11% ao ano"
        t2 = "Copom decide elevar taxa Selic para 11% nesta quarta"
        sim = token_similarity(normalize_title(t1), normalize_title(t2))
        self.assertGreaterEqual(sim, 0.35)

        now = datetime.now(timezone.utc)
        item1 = NewsItem(
            title=t1, link="http://uol.com/1", summary="Resumo 1",
            source_id="uol", source_name="UOL", category="Economia",
            published_at=now, language="pt"
        )
        item2 = NewsItem(
            title=t2, link="http://g1.com/2", summary="Resumo 2",
            source_id="g1", source_name="G1", category="Economia",
            published_at=now, language="pt"
        )

        clusters = cluster_and_deduplicate([item1, item2], similarity_threshold=0.4)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0].sources), 2)
        self.assertIn("UOL", clusters[0].sources)
        self.assertIn("G1", clusters[0].sources)

    def test_filter_by_time(self):
        """Verifica se itens antigos são descartados."""
        now = datetime.now(timezone.utc)
        recent = NewsItem(
            title="Recente", link="http://a.com", summary="",
            source_id="reuters", source_name="Reuters", category="Geral",
            published_at=now - timedelta(hours=2), language="en"
        )
        old = NewsItem(
            title="Antigo", link="http://b.com", summary="",
            source_id="reuters", source_name="Reuters", category="Geral",
            published_at=now - timedelta(hours=48), language="en"
        )

        filtered = filter_by_time([recent, old], hours=16)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Recente")

    def test_html_conversion(self):
        """Verifica a conversão de Markdown para HTML."""
        md = "# Título Principal\n\n- [Link Exemplo](https://reuters.com) *(Reuters)*"
        html_out = convert_markdown_to_html(md)
        self.assertIn("<html", html_out)
        self.assertIn("<h1>Título Principal</h1>", html_out)
        self.assertIn('href="https://reuters.com"', html_out)

    def test_whatsapp_formatting(self):
        """Verifica a conversão de Markdown para a sintaxe do WhatsApp."""
        from news_briefing.whatsapp_sender import markdown_to_whatsapp
        md = "# 🌅 Notícia\n- **[Destaque](https://g1.globo.com)**: Texto em negrito."
        wa = markdown_to_whatsapp(md)
        self.assertIn("*🌅 Notícia*", wa)
        self.assertIn("*Destaque (https://g1.globo.com)*", wa)


if __name__ == "__main__":
    unittest.main()
