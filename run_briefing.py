#!/usr/bin/env python3
"""
Briefing Geral de Notícias — Extrator RSS & Síntese com Google Gemini (3 Edições Diárias)
Fontes: Reuters, CNN, UOL, G1, BBC, InfoMoney e outros feeds.
Execuções recomendadas: 3 vezes ao dia (08:00, 13:00 e 19:00).
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
from news_briefing.formatters import save_markdown_report, save_html_report, render_terminal, archive_edition
from news_briefing.scheduler import run_at_schedule, generate_windows_task_cmd, DEFAULT_SCHEDULE_TIMES
from news_briefing.whatsapp_sender import send_whatsapp_message

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_default_lookback_hours() -> int:
    """Calcula a janela retroativa ideal em horas com base na hora atual para as 3 edições diárias."""
    current_hour = datetime.now().hour
    if current_hour < 11:
        return 14  # Edição da Manhã (08h): cobre noite anterior + começo do dia
    elif current_hour < 16:
        return 6   # Edição da Tarde (13h): cobre a manhã
    else:
        return 7   # Edição da Noite (19h): cobre a tarde


def run_pipeline(
    hours: int = None,
    selected_feeds: list = None,
    output_formats: list = None,
    model_name: str = DEFAULT_MODEL,
    api_key: str = None,
    dry_run: bool = False,
    send_whatsapp: bool = False
):
    """Executa o ciclo completo de coleta, filtragem, síntese e geração de relatórios."""
    effective_hours = hours if hours is not None else get_default_lookback_hours()
    reports_dir = ensure_reports_dir()
    all_feeds = load_configured_feeds()

    if selected_feeds:
        active_feeds = [f for f in all_feeds if f.get("id") in selected_feeds]
        if not active_feeds:
            console.print(f"[bold red]Nenhum feed correspondente aos IDs informados:[/bold red] {selected_feeds}")
            return
    else:
        active_feeds = all_feeds

    console.print(f"[bold cyan]📰 Iniciando Extração de Notícias (3 Edições Diárias)[/bold cyan]")
    console.print(f"📡 [cyan]Feeds selecionados:[/cyan] {', '.join([f['name'] for f in active_feeds])}")
    console.print(f"⏳ [cyan]Janela temporal:[/cyan] últimas {effective_hours} horas")

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
        task2 = progress.add_task(f"Filtrando notícias das últimas {effective_hours}h...", total=None)
        recent_items = filter_by_time(items, hours=effective_hours)
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
    table = Table(title="Top Histórias Identificadas no Período", show_lines=False, border_style="dim")
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

    # 6. Arquivamento Web (Catálogo Histórico da Vercel)
    web_entry = archive_edition(briefing_md, edition_type="nacional", filename_prefix="briefing")
    saved_files.append(f"Web Vercel: [bold underline]public/{web_entry['file']}[/bold underline]")

    # 6. Envio via WhatsApp (se solicitado via argumento ou habilitado no .env)
    should_wa = send_whatsapp or (os.getenv("WHATSAPP_ENABLED", "").lower() in ["true", "1", "yes"])
    if should_wa:
        console.print("\n[cyan]📱 Enviando briefing via WhatsApp...[/cyan]")
        ok = send_whatsapp_message(briefing_md)
        if ok:
            console.print("[bold green]✓ WhatsApp enviado com sucesso![/bold green]")
        else:
            console.print("[bold yellow]⚠️ Não foi possível enviar para o WhatsApp. Verifique WHATSAPP_PHONE e WHATSAPP_APIKEY no .env.[/bold yellow]")

    console.print("\n[bold green]🎉 Briefing de Notícias Concluído![/bold green]")
    for sf in saved_files:
        console.print(f"📄 Salvo em {sf}")


def main():
    parser = argparse.ArgumentParser(
        description="Briefing Geral de Notícias — 3 Edições Diárias (08h, 13h e 19h)"
    )
    parser.add_argument(
        "--morning",
        action="store_true",
        help="Executa a edição da manhã (últimas 14 horas de notícias)"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=None,
        help="Janela de tempo retroativa em horas (padrão: dinâmico - 14h de manhã, 6h de tarde, 7h de noite)"
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
        metavar="HH:MM,...",
        help="Executa nos horários agendados (padrão: 08:00,13:00,19:00 ou especifique horários separados por vírgula)"
    )
    parser.add_argument(
        "--register-task",
        type=str,
        default=None,
        metavar="HH:MM ou all",
        help="Gera o comando schtasks do Windows para automação (ex: 'all' para 08:00, 13:00 e 19:00, ou especifique HH:MM)"
    )
    parser.add_argument(
        "--whatsapp",
        action="store_true",
        help="Envia o relatório gerado para o WhatsApp (CallMeBot)"
    )
    parser.add_argument(
        "--test-whatsapp",
        action="store_true",
        help="Envia uma mensagem de teste para o WhatsApp configurado para validar"
    )

    args = parser.parse_args()

    # Se solicitou teste do WhatsApp
    if args.test_whatsapp:
        console.print("[cyan]Enviando mensagem de teste para o WhatsApp...[/cyan]")
        ok = send_whatsapp_message("👋 *Teste do News Briefing AI!* Seu canal de resumos de notícias no WhatsApp está configurado e pronto para uso.")
        if ok:
            console.print("[bold green]✓ Mensagem de teste enviada com sucesso ao seu WhatsApp![/bold green]")
        else:
            console.print("[bold red]Falha no envio do teste. Verifique se WHATSAPP_PHONE e WHATSAPP_APIKEY estão configurados no .env.[/bold red]")
        return

    # Se solicitou o comando do Windows Task Scheduler
    if args.register_task:
        script_path = str(Path(__file__).resolve())
        target_times = DEFAULT_SCHEDULE_TIMES if args.register_task.lower() in ["all", "3x", "default"] else [args.register_task]
        console.print("[bold cyan]Comandos para o Agendador de Tarefas do Windows (cmd como Administrador):[/bold cyan]\n")
        for t in target_times:
            cmd = generate_windows_task_cmd(script_path, t, task_prefix="BriefingNews")
            console.print(f"[green]{cmd}[/green]")
        console.print(f"\n[dim]Esses comandos criarão as tarefas para executar 3 vezes por dia ({', '.join(target_times)}).[/dim]")
        return

    selected_feeds = [f.strip() for f in args.feeds.split(",")] if args.feeds else None
    hours = 14 if args.morning else args.hours

    def job():
        run_pipeline(
            hours=hours,
            selected_feeds=selected_feeds,
            output_formats=[args.output],
            model_name=args.model,
            api_key=args.api_key,
            dry_run=args.dry_run,
            send_whatsapp=args.whatsapp
        )

    if args.schedule is not None or "--schedule" in sys.argv:
        sched_arg = args.schedule if args.schedule else "08:00,13:00,19:00"
        run_at_schedule(sched_arg, job)
    else:
        job()


if __name__ == "__main__":
    main()
