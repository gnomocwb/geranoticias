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


DEFAULT_SCHEDULE_TIMES = ["08:00", "13:00", "19:00"]


def parse_schedule_times(times_input) -> list:
    """Normaliza a entrada de horários para uma lista de strings HH:MM."""
    if not times_input:
        return DEFAULT_SCHEDULE_TIMES
    if isinstance(times_input, str):
        times_list = [t.strip() for t in times_input.split(",") if t.strip()]
        return times_list if times_list else DEFAULT_SCHEDULE_TIMES
    return list(times_input)


def run_at_schedule(target_times=None, job_func: Callable[[], None] = None):
    """
    Mantém um loop aguardando os horários configurados (padrão: 08:00, 13:00 e 19:00)
    para executar o resumo de notícias 3 vezes por dia.
    """
    times = parse_schedule_times(target_times)
    times_formatted = ", ".join(f"[bold yellow]{t}[/bold yellow]" for t in times)
    console.print(f"[bold green]⏰ Modo Agendado Ativado (3 Edições Diárias)![/bold green] Horários: {times_formatted}")
    console.print("[dim]Pressione Ctrl+C para encerrar o monitoramento.[/dim]\n")

    parsed_targets = [tuple(map(int, t.split(":"))) for t in times]

    while True:
        now = datetime.now()

        # Encontra o próximo horário mais próximo entre os alvos
        next_target = None
        for target_hour, target_minute in parsed_targets:
            candidate = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if candidate <= now:
                candidate += timedelta(days=1)
            if next_target is None or candidate < next_target:
                next_target = candidate

        wait_seconds = (next_target - now).total_seconds()
        console.print(f"[dim]Próxima edição em {wait_seconds / 3600:.1f}h ({next_target.strftime('%d/%m/%Y às %H:%M')})...[/dim]")

        # Espera com checagens frequentes
        time.sleep(min(wait_seconds, 60))

        now_check = datetime.now()
        for target_hour, target_minute in parsed_targets:
            if now_check.hour == target_hour and now_check.minute == target_minute:
                console.print(f"\n[bold cyan]🚀 Executando edição agendada ({now_check.strftime('%H:%M')})...[/bold cyan]")
                try:
                    job_func()
                except Exception as e:
                    console.print(f"[bold red]Erro na execução agendada:[/bold red] {e}")

                # Evita disparar duas vezes no mesmo minuto
                time.sleep(70)
                break


def generate_windows_task_cmd(script_path: str, time_str: str = "08:00", task_prefix: str = "BriefingNews") -> str:
    """
    Gera o comando oficial 'schtasks' do Windows para registrar tarefas automáticas.
    """
    python_exe = sys.executable
    time_tag = time_str.replace(":", "")[:4]
    task_name = f"{task_prefix}_{time_tag}"
    cmd = (
        f'schtasks /create /tn "{task_name}" /tr "\"{python_exe}\" \"{script_path}\" --output all" '
        f'/sc daily /st {time_str} /f'
    )
    return cmd
