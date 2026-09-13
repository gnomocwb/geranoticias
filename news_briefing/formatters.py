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


def convert_markdown_to_html(
    markdown_content: str,
    title: str = "Briefing Matinal de Notícias",
    badge_text: Optional[str] = None,
    footer_text: Optional[str] = None
) -> str:
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

    badge = badge_text or "☀️ Briefing Matinal Executivo"
    footer = footer_text or "Gerado automaticamente via RSS Feeds & Google Gemini • News Briefing AI"

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
      --accent-blue: #58a6ff;
      --accent-purple: #bc8cff;
      --accent-cyan: #39c5cf;
      --badge-bg: rgba(56, 139, 253, 0.15);
      --font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    body {{
      background-color: var(--bg-color);
      color: var(--text-main);
      font-family: var(--font-family);
      line-height: 1.65;
      margin: 0;
      padding: 40px 20px;
    }}

    .container {{
      max-width: 780px;
      margin: 0 auto;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 40px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
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
      font-size: 1.4rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      margin-top: 36px;
      margin-bottom: 16px;
      color: var(--accent-blue);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    h3 {{
      font-size: 1.15rem;
      font-weight: 600;
      margin-top: 24px;
      margin-bottom: 8px;
      color: var(--accent-purple);
    }}

    p {{
      margin: 12px 0;
      color: #c9d1d9;
    }}

    blockquote {{
      margin: 20px 0;
      padding: 12px 18px;
      background: rgba(110, 118, 129, 0.1);
      border-left: 4px solid var(--accent-blue);
      border-radius: 4px 8px 8px 4px;
      font-size: 0.95rem;
      color: var(--text-muted);
    }}

    blockquote p {{
      margin: 4px 0;
    }}

    ul {{
      padding-left: 20px;
      margin: 16px 0;
    }}

    li {{
      margin-bottom: 12px;
      color: #c9d1d9;
    }}

    strong {{
      color: #ffffff;
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
      <span class="badge">{badge}</span>
      <span class="date-pill">{datetime.now().strftime('%d/%m/%Y')}</span>
    </div>
    
    {inner_html}

    <div class="footer">
      {footer}
    </div>
  </div>
</body>
</html>
"""
    return full_html


def save_html_report(
    markdown_content: str,
    output_dir: Path,
    filename_prefix: str = "briefing",
    title: Optional[str] = None,
    badge_text: Optional[str] = None,
    footer_text: Optional[str] = None
) -> Path:
    """Salva o relatório em HTML moderno."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    html_path = output_dir / f"{filename_prefix}_{today_str}.html"

    if html_path.exists():
        timestamp = datetime.now().strftime("%H%M%S")
        html_path = output_dir / f"{filename_prefix}_{today_str}_{timestamp}.html"

    eff_title = title or ("Fatos da Região — Curitiba & Paraná" if "fatos" in filename_prefix else "Briefing Matinal de Notícias")
    eff_badge = badge_text or ("🏙️ Fatos da Região — Curitiba & Paraná" if "fatos" in filename_prefix else "☀️ Briefing Matinal Executivo")
    eff_footer = footer_text or ("Gerado via Tribuna do Paraná, Bem Paraná e Banda B & Google Gemini • Fatos da Região" if "fatos" in filename_prefix else "Gerado automaticamente via RSS Feeds & Google Gemini • News Briefing AI")

    html_content = convert_markdown_to_html(
        markdown_content,
        title=eff_title,
        badge_text=eff_badge,
        footer_text=eff_footer
    )
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
