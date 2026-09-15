#!/usr/bin/env python3
"""
Notícias Autismo Brasil — Giro Diário sobre o Transtorno do Espectro Autista (TEA) com Google Gemini
Fontes: Canal Autismo (Revista Autismo), Portais Nacionais, Agência Brasil & Decisões Jurídicas.
Execução recomendada: 1 vez ao dia (09:00 BRT, cobrindo as últimas 24 horas).
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Garante suporte a UTF-8 no Windows PowerShell/CMD
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

from news_briefing.config import (
    load_configured_feeds,
    ensure_reports_dir,
    get_api_key,
    DEFAULT_MODEL,
    DEFAULT_LANGUAGE
)
from news_briefing.fetcher import fetch_all_feeds
from news_briefing.deduplicator import filter_by_time, cluster_and_deduplicate
from news_briefing.gemini_synthesizer import (
    generate_autismo_briefing_with_gemini,
    generate_fallback_autismo_report
)
from news_briefing.formatters import save_markdown_report, save_html_report, archive_edition, get_now_brt
from news_briefing.scheduler import run_at_schedule
from news_briefing.whatsapp_sender import send_whatsapp_message

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

AUTISMO_FEEDS_FILE = Path(__file__).resolve().parent / "news_briefing" / "feeds_autismo.json"
DEFAULT_AUTISMO_SCHEDULE = "09:00"
DEFAULT_AUTISMO_HOURS = 24
DEFAULT_AUTISMO_REPORTS_DIR = Path(r"C:\Users\mlori\OneDrive\Documentos\Autismo")


def get_target_reports_dir(custom_path: str = None) -> Path:
    """Retorna o diretório de destino dos relatórios, priorizando a pasta do OneDrive no Windows."""
    if custom_path:
        target = Path(custom_path)
    elif os.getenv("AUTISMO_REPORTS_DIR"):
        target = Path(os.getenv("AUTISMO_REPORTS_DIR"))
    elif sys.platform == "win32":
        target = DEFAULT_AUTISMO_REPORTS_DIR
    else:
        target = ensure_reports_dir()

    try:
        target.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.warning(f"Não foi possível acessar/criar pasta de relatórios {target}: {e}. Usando pasta local.")
        target = ensure_reports_dir()

    return target


def run_pipeline(
    hours: int = DEFAULT_AUTISMO_HOURS,
    selected_feeds: list = None,
    output_formats: list = None,
    model_name: str = DEFAULT_MODEL,
    api_key: str = None,
    dry_run: bool = False,
    send_whatsapp: bool = False,
    output_dir: str = None
):
    """Executa o pipeline completo do Notícias Autismo Brasil."""
    effective_hours = hours or DEFAULT_AUTISMO_HOURS
    target_reports_dir = get_target_reports_dir(output_dir)
    local_reports_dir = ensure_reports_dir()
    all_feeds = load_configured_feeds(custom_file=AUTISMO_FEEDS_FILE)

    if selected_feeds:
        active_feeds = [f for f in all_feeds if f.get("id") in selected_feeds]
        if not active_feeds:
            console.print(f"[bold red]Nenhum feed de autismo correspondente aos IDs informados:[/bold red] {selected_feeds}")
            return
    else:
        active_feeds = all_feeds

    console.print(f"[bold cyan]🧩 Iniciando Notícias Autismo Brasil (Edição Diária 09h)[/bold cyan]")
    console.print(f"📡 [cyan]Canais & Buscas Monitoradas:[/cyan] {', '.join([f['name'] for f in active_feeds])}")
    console.print(f"⏳ [cyan]Janela temporal retroativa:[/cyan] últimas {effective_hours} horas")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        # 1. Coleta
        task1 = progress.add_task("Coletando matérias de autismo, direitos, inclusão e saúde...", total=None)
        items = fetch_all_feeds(active_feeds)
        progress.update(task1, completed=True)

        # 2. Filtro temporal (24h)
        task2 = progress.add_task(f"Filtrando publicações das últimas {effective_hours} horas...", total=None)
        recent_items = filter_by_time(items, hours=effective_hours)
        progress.update(task2, completed=True)

        # 3. Deduplicação e Agrupamento
        task3 = progress.add_task("Agrupando notícias similares e removendo duplicidades...", total=None)
        clusters = cluster_and_deduplicate(recent_items)
        progress.update(task3, completed=True)

    console.print(
        f"✓ [green]Coleta concluída:[/green] {len(items)} matérias brutas ➔ "
        f"{len(recent_items)} recentes ➔ [bold]{len(clusters)} histórias agrupadas[/bold]."
    )

    if not clusters:
        console.print("[yellow]Nenhuma notícia sobre autismo identificada na janela de tempo especificada.[/yellow]")
        return

    # Tabela resumo dos principais temas identificados
    table = Table(title="Destaques sobre Autismo no Brasil (Últimas 24h)", show_lines=False, border_style="dim")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Categoria", style="magenta")
    table.add_column("Notícia / Matéria", style="white")
    table.add_column("Fontes", style="green")

    for i, cl in enumerate(clusters[:10], 1):
        sources_str = ", ".join(cl.sources)
        table.add_row(str(i), cl.category, cl.primary_title[:75] + ("..." if len(cl.primary_title) > 75 else ""), sources_str)
    console.print(table)

    # 4. Síntese com Gemini ou Dry Run
    if dry_run:
        console.print("[yellow]Modo Dry-Run: Gerando relatório de autismo em agregação estruturada direta.[/yellow]")
        briefing_md = generate_fallback_autismo_report(clusters)
    else:
        effective_key = api_key or get_api_key()
        if not effective_key:
            console.print("[yellow]⚠️  Aviso: Nenhuma GEMINI_API_KEY detectada no .env ou argumentos.[/yellow]")
            console.print("[dim]Gerando relatório em modo fallback. Para IA, configure GEMINI_API_KEY no .env![/dim]")
            briefing_md = generate_fallback_autismo_report(clusters)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task4 = progress.add_task(f"Sintetizando 'Notícias Autismo Brasil' via Google Gemini ({model_name})...", total=None)
                briefing_md = generate_autismo_briefing_with_gemini(
                    stories=clusters,
                    api_key=effective_key,
                    model_name=model_name,
                    language=DEFAULT_LANGUAGE
                )
                progress.update(task4, completed=True)

    # 5. Geração e Exportação de Relatórios
    formats = output_formats or ["all"]
    saved_files = []

    if "all" in formats or "md" in formats:
        md_file = save_markdown_report(briefing_md, target_reports_dir, filename_prefix="noticias_autismo")
        saved_files.append(f"Markdown (OneDrive): [bold underline]{md_file}[/bold underline]")
        if target_reports_dir != local_reports_dir:
            save_markdown_report(briefing_md, local_reports_dir, filename_prefix="noticias_autismo")

    if "all" in formats or "html" in formats:
        html_file = save_html_report(
            briefing_md,
            target_reports_dir,
            filename_prefix="noticias_autismo",
            title="Notícias Autismo Brasil — Edição Diária (09h)",
            badge_text="🧩 Notícias Autismo Brasil • Edição Diária (09h)",
            footer_text="Gerado via Canal Autismo (Revista Autismo), Portais Nacionais & Google Gemini • Edição Diária às 09h"
        )
        saved_files.append(f"HTML (OneDrive): [bold underline]{html_file}[/bold underline]")
        if target_reports_dir != local_reports_dir:
            save_html_report(
                briefing_md,
                local_reports_dir,
                filename_prefix="noticias_autismo",
                title="Notícias Autismo Brasil — Edição Diária (09h)",
                badge_text="🧩 Notícias Autismo Brasil • Edição Diária (09h)",
                footer_text="Gerado via Canal Autismo (Revista Autismo), Portais Nacionais & Google Gemini • Edição Diária às 09h"
            )

    if "all" in formats or "cli" in formats:
        md = Markdown(briefing_md)
        console.print(
            Panel(
                md,
                title="[bold cyan]🧩 NOTÍCIAS AUTISMO BRASIL (EDIÇÃO DIÁRIA - 09H)[/bold cyan]",
                border_style="bright_blue",
                padding=(1, 2)
            )
        )

    # 6. Arquivamento Web (Catálogo da Vercel)
    if not dry_run:
        web_entry = archive_edition(briefing_md, edition_type="autismo", filename_prefix="noticias_autismo")
        saved_files.append(f"Web Vercel: [bold underline]public/{web_entry['file']}[/bold underline]")

    # 7. Envio via WhatsApp (se habilitado)
    should_wa = send_whatsapp or (os.getenv("WHATSAPP_ENABLED", "").lower() in ["true", "1", "yes"])
    if should_wa:
        console.print("\n[cyan]📱 Enviando 'Notícias Autismo Brasil' via WhatsApp...[/cyan]")
        ok = send_whatsapp_message(briefing_md)
        if ok:
            console.print("[bold green]✓ WhatsApp enviado com sucesso![/bold green]")
        else:
            console.print("[bold yellow]⚠️ Não foi possível enviar para o WhatsApp. Verifique suas configurações no .env.[/bold yellow]")

    console.print("\n[bold green]🎉 Notícias Autismo Brasil Concluído com Sucesso![/bold green]")
    for sf in saved_files:
        console.print(f"📄 Salvo em {sf}")


def main():
    parser = argparse.ArgumentParser(
        description="Notícias Autismo Brasil — Resumo Diário sobre TEA no Brasil (09:00 BRT)"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_AUTISMO_HOURS,
        help=f"Janela de tempo retroativa em horas (padrão: {DEFAULT_AUTISMO_HOURS} horas)"
    )
    parser.add_argument(
        "--feeds",
        type=str,
        default=None,
        help="IDs de feeds de autismo específicos separados por vírgula (ex: canal_autismo,gnews_autismo_direitos)"
    )
    parser.add_argument(
        "--output",
        choices=["all", "md", "html", "cli"],
        default="all",
        help="Formato de saída do relatório (padrão: all)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Modelo do Gemini a utilizar (padrão: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Chave Gemini explícita (opcional, lida do .env)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa coleta e agregação sem chamada de IA"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help=f"Diretório onde salvar os relatórios (padrão: {DEFAULT_AUTISMO_REPORTS_DIR})"
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default=None,
        metavar="HH:MM",
        help=f"Executa no horário diário agendado (padrão: {DEFAULT_AUTISMO_SCHEDULE})"
    )
    parser.add_argument(
        "--register-task",
        type=str,
        default=None,
        metavar="HH:MM",
        help="Gera o comando schtasks do Windows para automação diária (ex: '09:00')"
    )
    parser.add_argument(
        "--whatsapp",
        action="store_true",
        help="Envia o relatório gerado para o WhatsApp configurado"
    )
    parser.add_argument(
        "--test-whatsapp",
        action="store_true",
        help="Envia uma mensagem de teste para o WhatsApp configurado"
    )

    args = parser.parse_args()

    if args.test_whatsapp:
        console.print("[cyan]Enviando teste para o WhatsApp...[/cyan]")
        ok = send_whatsapp_message("👋 *Teste do Notícias Autismo Brasil!* Seu boletim diário sobre TEA está configurado.")
        if ok:
            console.print("[bold green]✓ Mensagem de teste enviada com sucesso ao seu WhatsApp![/bold green]")
        else:
            console.print("[bold red]Falha no envio do teste. Verifique suas chaves no .env.[/bold red]")
        return

    if args.register_task:
        target_time = args.register_task if ":" in args.register_task else DEFAULT_AUTISMO_SCHEDULE
        script_path = str(Path(__file__).resolve())
        venv_python = Path(sys.executable).resolve()
        time_tag = target_time.replace(":", "")[:4]
        task_name = f"NoticiasAutismo_{time_tag}"
        cmd = f'schtasks /create /tn "{task_name}" /tr "\"{venv_python}\" \"{script_path}\"" /sc daily /st {target_time} /f'
        console.print("[bold cyan]Comando para o Agendador de Tarefas do Windows (execute no Prompt como Administrador):[/bold cyan]\n")
        console.print(f"[green]{cmd}[/green]")
        console.print(f"\n[dim]Esse comando criará uma tarefa diária para rodar todos os dias às {target_time}.[/dim]")
        return

    selected_feeds = [f.strip() for f in args.feeds.split(",")] if args.feeds else None

    def job():
        run_pipeline(
            hours=args.hours,
            selected_feeds=selected_feeds,
            output_formats=[args.output],
            model_name=args.model,
            api_key=args.api_key,
            dry_run=args.dry_run,
            send_whatsapp=args.whatsapp,
            output_dir=args.output_dir
        )

    if args.schedule is not None or "--schedule" in sys.argv:
        sched_arg = args.schedule if args.schedule else DEFAULT_AUTISMO_SCHEDULE
        run_at_schedule(sched_arg, job)
    else:
        job()


if __name__ == "__main__":
    main()
