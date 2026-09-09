#!/usr/bin/env python3
"""
Briefing Matinal de Notícias — Extrator RSS & Síntese com Google Gemini
Fontes: Reuters, CNN, UOL, G1, BBC, InfoMoney e outros feeds.
"""

import sys
import argparse
import logging
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

from news_briefing.config import (
    load_configured_feeds,
    ensure_reports_dir,
    get_api_key,
    DEFAULT_MODEL,
    DEFAULT_HOURS,
    DEFAULT_LANGUAGE
)
from news_briefing.fetcher import fetch_all_feeds
from news_briefing.deduplicator import filter_by_time, cluster_and_deduplicate
from news_briefing.gemini_synthesizer import generate_briefing_with_gemini, generate_fallback_report
from news_briefing.formatters import save_markdown_report, save_html_report, render_terminal
from news_briefing.scheduler import run_at_schedule, generate_windows_task_cmd

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_pipeline(
    hours: int = 16,
    selected_feeds: list = None,
    output_formats: list = None,
    model_name: str = DEFAULT_MODEL,
    api_key: str = None,
    dry_run: bool = False
):
    """Executa o ciclo completo de coleta, filtragem, síntese e geração de relatórios."""
    reports_dir = ensure_reports_dir()
    all_feeds = load_configured_feeds()

    if selected_feeds:
        active_feeds = [f for f in all_feeds if f.get("id") in selected_feeds]
        if not active_feeds:
            console.print(f"[bold red]Nenhum feed correspondente aos IDs informados:[/bold red] {selected_feeds}")
            return
    else:
        active_feeds = all_feeds

    console.print(f"[bold cyan]☀️ Iniciando Extração Matinal de Notícias[/bold cyan]")
    console.print(f"📡 [cyan]Feeds selecionados:[/cyan] {', '.join([f['name'] for f in active_feeds])}")
    console.print(f"⏳ [cyan]Janela temporal:[/cyan] últimas {hours} horas")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        # 1. Coleta
        task1 = progress.add_task("Coletando feeds RSS paralelamente...", total=None)
        items = fetch_all_feeds(active_feeds)
        progress.update(task1, completed=True)

        # 2. Filtro temporal
        task2 = progress.add_task(f"Filtrando notícias das últimas {hours}h...", total=None)
        recent_items = filter_by_time(items, hours=hours)
        progress.update(task2, completed=True)

        # 3. Deduplicação e Agrupamento
        task3 = progress.add_task("Agrupando histórias e deduplicando manchetes...", total=None)
        clusters = cluster_and_deduplicate(recent_items)
        progress.update(task3, completed=True)

    console.print(
        f"✓ [green]Coleta finalizada:[/green] {len(items)} itens brutos ➔ "
        f"{len(recent_items)} notícias recentes ➔ [bold]{len(clusters)} histórias agrupadas[/bold]."
    )

    if not clusters:
        console.print("[yellow]Nenhuma notícia encontrada no período especificado.[/yellow]")
        return

    # Tabela resumo das principais histórias
    table = Table(title="Top Histórias Identificadas nesta Manhã", show_lines=False, border_style="dim")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Categoria", style="magenta")
    table.add_column("Título", style="white")
    table.add_column("Fontes", style="green")

    for i, cl in enumerate(clusters[:8], 1):
        sources_str = ", ".join(cl.sources)
        table.add_row(str(i), cl.category, cl.primary_title[:75] + ("..." if len(cl.primary_title) > 75 else ""), sources_str)
    console.print(table)

    # 4. Síntese com Gemini ou Dry Run
    if dry_run:
        console.print("[yellow]Modo Dry-Run ativado: Gerando relatório estruturado direto sem chamar IA.[/yellow]")
        briefing_md = generate_fallback_report(clusters)
    else:
        effective_key = api_key or get_api_key()
        if not effective_key:
            console.print("[yellow]⚠️  Aviso: Nenhuma GEMINI_API_KEY detectada no .env ou argumentos.[/yellow]")
            console.print("[dim]Gerando relatório com agregação estruturada. Para IA, configure seu .env![/dim]")
            briefing_md = generate_fallback_report(clusters)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task4 = progress.add_task(f"Sintetizando briefing executivo via Google Gemini ({model_name})...", total=None)
                briefing_md = generate_briefing_with_gemini(
                    stories=clusters,
                    api_key=effective_key,
                    model_name=model_name,
                    language=DEFAULT_LANGUAGE
                )
                progress.update(task4, completed=True)

    # 5. Geração e Exportação
    formats = output_formats or ["all"]
    saved_files = []

    if "all" in formats or "md" in formats:
        md_file = save_markdown_report(briefing_md, reports_dir)
        saved_files.append(f"Markdown: [bold underline]{md_file}[/bold underline]")

    if "all" in formats or "html" in formats:
        html_file = save_html_report(briefing_md, reports_dir)
        saved_files.append(f"HTML: [bold underline]{html_file}[/bold underline]")

    if "all" in formats or "cli" in formats:
        render_terminal(briefing_md)

    console.print("\n[bold green]🎉 Briefing Matinal Concluído![/bold green]")
    for sf in saved_files:
        console.print(f"📄 Salvo em {sf}")


def main():
    parser = argparse.ArgumentParser(
        description="Extração matinal de notícias via RSS e síntese com Google Gemini"
    )
    parser.add_argument(
        "--morning",
        action="store_true",
        help="Executa o perfil matinal padrão (últimas 16 horas de notícias)"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_HOURS,
        help="Janela de tempo retroativa em horas (padrão: 16)"
    )
    parser.add_argument(
        "--feeds",
        type=str,
        default=None,
        help="IDs de feeds específicos separados por vírgula (ex: reuters,cnn_brasil,uol_noticias)"
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
        help="Modelo do Gemini a utilizar (padrão: gemini-2.5-flash)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Chave Gemini explícita (opcional, pode ser configurada via GEMINI_API_KEY no .env)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas coleta e monta o relatório sem fazer chamada à API Gemini"
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default=None,
        metavar="HH:MM",
        help="Ativa o agendamento contínuo para executar diariamente no horário informado (ex: 07:00)"
    )
    parser.add_argument(
        "--register-task",
        type=str,
        default=None,
        metavar="HH:MM",
        help="Exibe o comando do Agendador de Tarefas do Windows para automação às HH:MM"
    )

    args = parser.parse_args()

    # Se solicitou o comando do Windows Task Scheduler
    if args.register_task:
        script_path = str(Path(__file__).resolve())
        cmd = generate_windows_task_cmd(script_path, args.register_task)
        console.print("[bold cyan]Comando para o Agendador de Tarefas do Windows (cmd como Administrador):[/bold cyan]")
        console.print(f"\n[green]{cmd}[/green]\n")
        console.print("[dim]Esse comando criará a tarefa 'BriefingMatinalNews' que roda todo dia às " + args.register_task + ".[/dim]")
        return

    selected_feeds = [f.strip() for f in args.feeds.split(",")] if args.feeds else None
    hours = 16 if args.morning else args.hours

    def job():
        run_pipeline(
            hours=hours,
            selected_feeds=selected_feeds,
            output_formats=[args.output],
            model_name=args.model,
            api_key=args.api_key,
            dry_run=args.dry_run
        )

    if args.schedule:
        run_at_schedule(args.schedule, job)
    else:
        job()


if __name__ == "__main__":
    main()
