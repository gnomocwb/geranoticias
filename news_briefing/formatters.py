import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console(highlight=False)


def save_markdown_report(content: str, output_dir: Path, filename_prefix: str = "briefing") -> Path:
    """Salva o briefing em formato Markdown (.md)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    md_path = output_dir / f"{filename_prefix}_{today_str}.md"

    # Se já existir um arquivo hoje, cria com timestamp para não sobrescrever acidentalmente
    if md_path.exists():
        timestamp = datetime.now().strftime("%H%M%S")
        md_path = output_dir / f"{filename_prefix}_{today_str}_{timestamp}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    return md_path


def convert_markdown_to_html(markdown_content: str, title: str = "Briefing Matinal de Notícias") -> str:
    """Converte o texto Markdown em um HTML executivo, responsivo e moderno."""
    # Conversões simples de Markdown para HTML básico
    html_body = markdown_content

    # Escapar quebras e títulos
    html_body = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html_body, flags=re.MULTILINE)

    # Citações blockquote
    html_body = re.sub(r"^> (.*?)$", r"<blockquote>\1</blockquote>", html_body, flags=re.MULTILINE)

    # Linha divisória
    html_body = re.sub(r"^---$", r"<hr/>", html_body, flags=re.MULTILINE)

    # Links: [texto](url)
    html_body = re.sub(r"\[(.*?)\]\((https?://.*?)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', html_body)

    # Negrito e Itálico
    html_body = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html_body)
    html_body = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html_body)

    # Listas
    lines = html_body.split("\n")
    in_list = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            if not in_list:
                new_lines.append("<ul>")
                in_list = True
            item_content = stripped[2:]
            new_lines.append(f"<li>{item_content}</li>")
        else:
            if in_list:
                new_lines.append("</ul>")
                in_list = False
            if stripped and not stripped.startswith("<h") and not stripped.startswith("<hr") and not stripped.startswith("<block"):
                new_lines.append(f"<p>{line}</p>")
            else:
                new_lines.append(line)
    if in_list:
        new_lines.append("</ul>")

    inner_html = "\n".join(new_lines)

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — {datetime.now().strftime('%d/%m/%Y')}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-color: #0d1117;
      --card-bg: #161b22;
      --border-color: #30363d;
      --text-main: #e6edf3;
      --text-muted: #8b949e;
      --accent-blue: #388bfd;
      --accent-cyan: #39c5cf;
      --accent-amber: #d29922;
      --accent-green: #3fb950;
      --badge-bg: rgba(56, 139, 253, 0.15);
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    @media (prefers-color-scheme: light) {{
      :root {{
        --bg-color: #f6f8fa;
        --card-bg: #ffffff;
        --border-color: #d0d7de;
        --text-main: #1f2328;
        --text-muted: #656d76;
        --accent-blue: #0969da;
        --accent-cyan: #0550ae;
        --badge-bg: #ddf4ff;
      }}
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      background-color: var(--bg-color);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.65;
      padding: 40px 20px;
      display: flex;
      justify-content: center;
    }}

    .container {{
      max-width: 860px;
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 48px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }}

    .top-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 16px;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--badge-bg);
      color: var(--accent-blue);
      font-weight: 600;
      font-size: 0.85rem;
      padding: 4px 12px;
      border-radius: 20px;
    }}

    .date-pill {{
      font-size: 0.85rem;
      color: var(--text-muted);
      font-weight: 500;
    }}

    h1 {{
      font-size: 2.1rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 16px;
      color: var(--text-main);
      line-height: 1.25;
    }}

    h2 {{
      font-size: 1.45rem;
      font-weight: 700;
      margin-top: 36px;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--border-color);
      color: var(--accent-blue);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    h3 {{
      font-size: 1.15rem;
      font-weight: 600;
      margin-top: 20px;
      margin-bottom: 8px;
    }}

    blockquote {{
      background: rgba(56, 139, 253, 0.08);
      border-left: 4px solid var(--accent-blue);
      padding: 12px 18px;
      border-radius: 0 8px 8px 0;
      margin: 16px 0 24px 0;
      color: var(--text-muted);
      font-size: 0.95rem;
    }}

    p {{
      margin-bottom: 14px;
      color: var(--text-main);
    }}

    ul {{
      list-style-type: none;
      margin-bottom: 20px;
    }}

    li {{
      position: relative;
      padding-left: 24px;
      margin-bottom: 12px;
    }}

    li::before {{
      content: "•";
      position: absolute;
      left: 6px;
      color: var(--accent-blue);
      font-size: 1.3rem;
      line-height: 1;
    }}

    strong {{
      color: var(--text-main);
      font-weight: 600;
    }}

    a {{
      color: var(--accent-blue);
      text-decoration: none;
      font-weight: 500;
      transition: color 0.15s ease;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    hr {{
      border: none;
      height: 1px;
      background: var(--border-color);
      margin: 32px 0;
    }}

    .footer {{
      margin-top: 40px;
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border-color);
      padding-top: 20px;
    }}

    @media (max-width: 640px) {{
      .container {{ padding: 24px 18px; }}
      h1 {{ font-size: 1.6rem; }}
      h2 {{ font-size: 1.25rem; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="top-bar">
      <span class="badge">☀️ Briefing Matinal Executivo</span>
      <span class="date-pill">{datetime.now().strftime('%A, %d de %B de %Y')}</span>
    </div>
    
    {inner_html}

    <div class="footer">
      Gerado automaticamente via RSS Feeds (Reuters, CNN, UOL, G1, BBC) & Google Gemini • News Briefing AI
    </div>
  </div>
</body>
</html>
"""
    return full_html


def save_html_report(markdown_content: str, output_dir: Path, filename_prefix: str = "briefing") -> Path:
    """Salva o relatório em HTML moderno."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    html_path = output_dir / f"{filename_prefix}_{today_str}.html"

    if html_path.exists():
        timestamp = datetime.now().strftime("%H%M%S")
        html_path = output_dir / f"{filename_prefix}_{today_str}_{timestamp}.html"

    html_content = convert_markdown_to_html(markdown_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_path


def render_terminal(markdown_content: str):
    """Exibe o relatório formatado com Rich no terminal."""
    md = Markdown(markdown_content)
    console.print(
        Panel(
            md,
            title="[bold cyan]🌅 BRIEFING MATINAL DE NOTÍCIAS[/bold cyan]",
            border_style="bright_blue",
            padding=(1, 2)
        )
    )
