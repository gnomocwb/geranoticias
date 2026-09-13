import os
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Caminho para o catálogo de dados no ambiente Linux da Vercel
        base_dir = Path(__file__).resolve().parent.parent
        index_file = base_dir / "public" / "data" / "archive_index.json"

        editions = []
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    editions = json.load(f)
            except Exception:
                pass

        payload = {
            "status": "online",
            "service": "News Briefing AI & Fatos da Região API",
            "runtime": "Vercel Python Serverless (Linux)",
            "total_editions": len(editions),
            "latest_edition": editions[0] if editions else None
        }

        self.wfile.write(json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8'))
        return
