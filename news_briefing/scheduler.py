import sys
import time
import subprocess
from datetime import datetime, timedelta
from typing import Callable

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console

console = Console(highlight=False)


def run_at_schedule(target_time_str: str, job_func: Callable[[], None]):
    """
    Mantém um loop aguardando o horário configurado (ex: '07:00') para executar o briefing matinal todos os dias.
    """
    console.print(f"[bold green]⏰ Modo Agendado Ativado![/bold green] O briefing será gerado diariamente às [bold yellow]{target_time_str}[/bold yellow].")
    console.print("[dim]Pressione Ctrl+C para encerrar o monitoramento.[/dim]\n")

    target_hour, target_minute = map(int, target_time_str.split(":"))

    while True:
        now = datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        console.print(f"[dim]Próxima execução em {wait_seconds / 3600:.1f} horas ({target.strftime('%d/%m/%Y às %H:%M')})...[/dim]")

        # Espera até o horário
        time.sleep(min(wait_seconds, 60))

        now_check = datetime.now()
        if now_check.hour == target_hour and now_check.minute == target_minute:
            console.print(f"\n[bold cyan]🚀 Executando briefing matinal agendado ({now_check.strftime('%H:%M')})...[/bold cyan]")
            try:
                job_func()
            except Exception as e:
                console.print(f"[bold red]Erro na execução agendada:[/bold red] {e}")

            # Evita disparar duas vezes no mesmo minuto
            time.sleep(70)


def generate_windows_task_cmd(script_path: str, time_str: str = "07:00") -> str:
    """
    Gera o comando oficial 'schtasks' do Windows para registrar uma tarefa matinal automática.
    """
    python_exe = sys.executable
    cmd = (
        f'schtasks /create /tn "BriefingMatinalNews" /tr "\"{python_exe}\" \"{script_path}\" --morning --output all" '
        f'/sc daily /st {time_str} /f'
    )
    return cmd
