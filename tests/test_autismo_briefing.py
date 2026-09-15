import unittest
from datetime import datetime, timezone
from pathlib import Path

from news_briefing.config import load_configured_feeds
from news_briefing.deduplicator import ClusteredStory
from news_briefing.fetcher import NewsItem
from news_briefing.gemini_synthesizer import generate_fallback_autismo_report
from news_briefing.formatters import save_html_report, save_markdown_report


class TestAutismoBriefing(unittest.TestCase):

    def setUp(self):
        self.autismo_feeds_path = Path(__file__).resolve().parent.parent / "news_briefing" / "feeds_autismo.json"

    def test_feeds_autismo_json_loads(self):
        """Verifica se o arquivo feeds_autismo.json existe, carrega e é válido."""
        self.assertTrue(self.autismo_feeds_path.exists())
        feeds = load_configured_feeds(custom_file=self.autismo_feeds_path)
        self.assertGreater(len(feeds), 0)

        expected_ids = [
            "canal_autismo",
            "gnews_autismo_geral",
            "gnews_autismo_direitos",
            "gnews_autismo_educacao",
            "gnews_autismo_ciencia"
        ]
        loaded_ids = [f["id"] for f in feeds]
        for eid in expected_ids:
            self.assertIn(eid, loaded_ids)

        for feed in feeds:
            self.assertIn("id", feed)
            self.assertIn("name", feed)
            self.assertIn("url", feed)
            self.assertIn("category", feed)
            self.assertTrue(feed["url"].startswith("http"))
            self.assertTrue(feed.get("enabled", True))

    def test_canal_autismo_feed_url(self):
        """Verifica se o Canal Autismo (Revista Autismo) está apontando para o feed oficial."""
        feeds = load_configured_feeds(custom_file=self.autismo_feeds_path)
        canal = next(f for f in feeds if f["id"] == "canal_autismo")
        self.assertEqual(canal["url"], "https://canalautismo.com.br/feed/")
        self.assertEqual(canal["category"], "Especializado")

    def test_generate_fallback_autismo_report(self):
        """Testa se a geração de relatório estruturado para autismo funciona sem erros."""
        now = datetime.now(timezone.utc)
        item1 = NewsItem(
            title="STJ decide sobre cobertura obrigatória de terapias para autismo",
            link="https://exemplo.com/noticia-stj",
            summary="Decisão importante fixa precedentes sobre planos de saúde e cobertura multidisciplinar.",
            source_id="gnews_autismo_direitos",
            source_name="Google News",
            category="Direitos & Legislação",
            published_at=now,
            language="pt"
        )
        item2 = NewsItem(
            title="Escolas públicas ampliam atendimento educacional especializado para TEA",
            link="https://exemplo.com/noticia-educacao",
            summary="Capacitação de professores e contratação de mediadores escolares.",
            source_id="gnews_autismo_educacao",
            source_name="Canal Autismo",
            category="Educação & Inclusão",
            published_at=now,
            language="pt"
        )

        cluster1 = ClusteredStory(item1)
        cluster2 = ClusteredStory(item2)

        report = generate_fallback_autismo_report([cluster1, cluster2])
        self.assertIn("Notícias Autismo Brasil", report)
        self.assertIn("Edição Diária (09h)", report)
        self.assertIn("STJ decide sobre cobertura obrigatória", report)
        self.assertIn("Escolas públicas ampliam", report)
        self.assertIn("⚖️ Direitos & Legislação", report)
        self.assertIn("🏫 Educação & Inclusão", report)

    def test_save_autismo_html_report(self):
        """Verifica se o relatório HTML de autismo é gravado com o badge e título corretos."""
        test_dir = Path(__file__).resolve().parent.parent / "reports" / "test_temp"
        sample_md = "# 🧩 Notícias Autismo Brasil\n\n- **[Teste](https://exemplo.com)**: Matéria de teste."
        html_file = save_html_report(sample_md, test_dir, filename_prefix="noticias_autismo")

        self.assertTrue(html_file.exists())
        content = html_file.read_text(encoding="utf-8")
        self.assertIn("Notícias Autismo Brasil — Edição Diária (09h)", content)
        self.assertIn("🧩 Notícias Autismo Brasil • Edição Diária (09h)", content)

        # Limpa arquivo temporário
        if html_file.exists():
            html_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
