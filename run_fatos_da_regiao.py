#!/usr/bin/env python3
"""
Fatos da Região — Briefing Matinal de Curitiba, RMC e Paraná com Google Gemini
Fontes: Tribuna do Paraná, Bem Paraná e Banda B.
Execução recomendada: Diariamente às 09:00 (cobrindo o dia anterior e o começo da manhã).
"""

import sys
import os
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
    generate_regional_briefing_with_gemini,
    generate_fallback_regional_report
)
from news_briefing.formatters import save_markdown_report, save_html_report
from news_briefing.scheduler import run_at_schedule, generate_windows_task_cmd
from news_briefing.whatsapp_sender import send_whatsapp_message

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

REGIONAL_FEEDS_FILE = Path(__file__).resolve().parent / "news_briefing" / "feeds_regional.json"
DEFAULT_REGIONAL_HOURS = 22  # Janela ideal às 09:00: cobre a tarde/noite do dia anterior e a manhã atual


def run_pipeline(
    hours: int = DEFAULT_REGIONAL_HOURS,
    selected_feeds: list = None,
    output_formats: list = None,
    model_name: str = DEFAULT_MODEL,
    api_key: str = None,
    dry_run: bool = False,
    send_whatsapp: bool = False
):
    """Executa o pipeline completo do Fatos da Região (Curitiba, RMC e Paraná)."""
    reports_dir = ensure_reports_dir()
    all_feeds = load_configured_feeds(custom_file=REGIONAL_FEEDS_FILE)

    if selected_feeds:
        active_feeds = [f for f in all_feeds if f.get("id") in selected_feeds]
        if not active_feeds:
            console.print(f"[bold red]Nenhum feed regional correspondente aos IDs informados:[/bold red] {selected_feeds}")
            return
    else:
        active_feeds = all_feeds

    console.print(f"[bold cyan]🏙️ Iniciando Fatos da Região — Curitiba & Paraná[/bold cyan]")
    console.print(f"📡 [cyan]Portais Ativos:[/cyan] {', '.join([f['name'] for f in active_feeds])}")
    console.print(f"⏳ [cyan]Janela temporal:[/cyan] últimas {hours} horas (dia anterior + início da manhã)")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        # 1. Coleta
        task1 = progress.add_task("Coletando notícias de Tribuna PR, Bem Paraná e Banda B...", total=None)
        items = fetch_all_feeds(active_feeds)
        progress.update(task1, completed=True)

        # 2. Filtro temporal
        task2 = progress.add_task(f"Filtrando ocorrências e notícias das últimas {hours}h...", total=None)
        recent_items = filter_by_time(items, hours=hours)
        progress.update(task2, completed=True)

        # 3. Deduplicação e Agrupamento
        task3 = progress.add_task("Deduplicando coberturas simultâneas da região...", total=None)
        clusters = cluster_and_deduplicate(recent_items)
        progress.update(task3, completed=True)

    console.print(
        f"✓ [green]Coleta regional concluída:[/green] {len(items)} matérias brutas ➔ "
        f"{len(recent_items)} recentes ➔ [bold]{len(clusters)} histórias locais agrupadas[/bold]."
    )

    if not clusters:
        console.print("[yellow]Nenhuma notícia regional encontrada no período especificado.[/yellow]")
        return

    # Tabela resumo das principais histórias regionais
    table = Table(title="Destaques Identificados em Curitiba, RMC e Paraná", show_lines=False, border_style="dim")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Categoria", style="magenta")
    table.add_column("Notícia / Ocorrência", style="white")
    table.add_column("Fontes", style="green")

    for i, cl in enumerate(clusters[:10], 1):
        sources_str = ", ".join(cl.sources)
        table.add_row(str(i), cl.category, cl.primary_title[:75] + ("..." if len(cl.primary_title) > 75 else ""), sources_str)
    console.print(table)

    # 4. Síntese com Gemini ou Dry Run
    if dry_run:
        console.print("[yellow]Modo Dry-Run: Gerando Fatos da Região com agregação direta estruturada.[/yellow]")
        briefing_md = generate_fallback_regional_report(clusters)
    else:
        effective_key = api_key or get_api_key()
        if not effective_key:
            console.print("[yellow]⚠️  Aviso: Nenhuma GEMINI_API_KEY detectada no .env ou argumentos.[/yellow]")
            console.print("[dim]Gerando relatório em modo fallback. Para IA, configure sua chave no .env![/dim]")
            briefing_md = generate_fallback_regional_report(clusters)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task4 = progress.add_task(f"Sintetizando 'Fatos da Região' via Google Gemini ({model_name})...", total=None)
                briefing_md = generate_regional_briefing_with_gemini(
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
        md_file = save_markdown_report(briefing_md, reports_dir, filename_prefix="fatos_da_regiao")
        saved_files.append(f"Markdown: [bold underline]{md_file}[/bold underline]")

    if "all" in formats or "html" in formats:
        html_file = save_html_report(
            briefing_md,
            reports_dir,
            filename_prefix="fatos_da_regiao",
            title="Fatos da Região — Curitiba & Paraná",
            badge_text="🏙️ Fatos da Região — Curitiba & Paraná",
            footer_text="Gerado via Tribuna do Paraná, Bem Paraná e Banda B & Google Gemini • Fatos da Região"
        )
        saved_files.append(f"HTML: [bold underline]{html_file}[/bold underline]")

    if "all" in formats or "cli" in formats:
        md = Markdown(briefing_md)
        console.print(
            Panel(
                md,
                title="[bold cyan]🏙️ FATOS DA REGIÃO — CURITIBA & PARANÁ[/bold cyan]",
                border_style="bright_blue",
                padding=(1, 2)
            )
        )

    # 6. Envio via WhatsApp (se habilitado)
    should_wa = send_whatsapp or (os.getenv("WHATSAPP_ENABLED", "").lower() in ["true", "1", "yes"])
    if should_wa:
        console.print("\n[cyan]📱 Enviando 'Fatos da Região' via WhatsApp...[/cyan]")
        ok = send_whatsapp_message(briefing_md)
        if ok:
            console.print("[bold green]✓ WhatsApp enviado com sucesso![/bold green]")
        else:
            console.print("[bold yellow]⚠️ Não foi possível enviar para o WhatsApp. Verifique suas configurações no .env.[/bold yellow]")

    console.print("\n[bold green]🎉 Fatos da Região Concluído com Sucesso![/bold green]")
    for sf in saved_files:
        console.print(f"📄 Salvo em {sf}")


def main():
    parser = argparse.ArgumentParser(
        description="Fatos da Região — Notícias de Curitiba e Paraná via Tribuna PR, Bem Paraná e Banda B com Google Gemini"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_REGIONAL_HOURS,
        help=f"Janela de tempo retroativa em horas (padrão: {DEFAULT_REGIONAL_HOURS}, ideal para cobrir dia anterior e início da manhã)"
    )
    parser.add_argument(
        "--feeds",
        type=str,
        default=None,
        help="IDs de feeds regionais específicos separados por vírgula (ex: tribunapr_direct,bemparana_direct,bandab_direct)"
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
        help="Chave Gemini explícita (opcional, pode ser lida do .env)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa coleta e agregação sem chamada de IA"
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default=None,
        metavar="HH:MM",
        help="Executa o pipeline diariamente no horário agendado (ex: 09:00)"
    )
    parser.add_argument(
        "--register-task",
        type=str,
        default=None,
        metavar="HH:MM",
        help="Exibe o comando do Agendador de Tarefas do Windows para executar às HH:MM (ex: 09:00)"
    )
    parser.add_argument(
        "--whatsapp",
        action="store_true",
        help="Envia o relatório gerado para o WhatsApp"
    )
    parser.add_argument(
        "--test-whatsapp",
        action="store_true",
        help="Envia uma mensagem de teste para o WhatsApp configurado"
    )

    args = parser.parse_args()

    if args.test_whatsapp:
        console.print("[cyan]Enviando teste para o WhatsApp...[/cyan]")
        ok = send_whatsapp_message("👋 *Teste do Fatos da Região!* Seu boletim regional de notícias do Paraná está configurado.")
        if ok:
            console.print("[bold green]✓ Mensagem de teste enviada com sucesso ao seu WhatsApp![/bold green]")
        else:
            console.print("[bold red]Falha no envio do teste. Verifique suas chaves no .env.[/bold red]")
        return

    if args.register_task:
        script_path = str(Path(__file__).resolve())
        # Cria a tarefa com nome diferenciado FatosDaRegiaoBriefing
        venv_python = Path(sys.executable).resolve()
        task_name = "FatosDaRegiaoBriefing"
        cmd = f'schtasks /create /tn "{task_name}" /tr "\"{venv_python}\" \"{script_path}\" --hours {args.hours}" /sc daily /st {args.register_task} /f'
        console.print("[bold cyan]Comando para o Agendador de Tarefas do Windows (cmd como Administrador):[/bold cyan]")
        console.print(f"\n[green]{cmd}[/green]\n")
        console.print(f"[dim]Esse comando criará a tarefa '{task_name}' que roda diariamente às {args.register_task}.[/dim]")
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
            send_whatsapp=args.whatsapp
        )

    if args.schedule:
        console.print(f"[bold cyan]⏰ Modo Agendador Ativado:[/bold cyan] Executando diariamente às [bold green]{args.schedule}[/bold green]...")
        run_at_schedule(args.schedule, job)
    else:
        job()


if __name__ == "__main__":
    main()
