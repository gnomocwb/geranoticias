@echo off
setlocal
cd /d "C:\Users\mlori\toco\antigravity"

echo ======================================================
echo [%date% %time%] Executando Edicoes Agendadas
echo ======================================================

echo Sincronizando com o GitHub...
git pull origin main

echo [1/3] Executando Fatos da Regiao (Curitiba ^& PR)...
"C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" run_fatos_da_regiao.py

echo [2/3] Executando Noticias Brasil ^& Mundo...
"C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" run_briefing.py

echo [3/3] Executando Noticias Autismo Brasil...
"C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" run_noticias_autismo.py

echo Enviando atualizacoes para o GitHub / Vercel...
git add public/data/ reports/
git diff --staged --quiet
if errorlevel 1 (
    git commit -m "chore(auto): novas edicoes agendadas publicadas [skip ci]"
    git push origin main
    if errorlevel 1 (
        echo Push direto rejeitado. Sincronizando e resolvendo catalogo...
        git pull origin main --no-rebase -X theirs
        "C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" scripts\resolve_archive_index.py
        git add public/data/archive_index.json
        git diff --staged --quiet || git commit -m "chore(merge): sincroniza catalogo de edicoes [skip ci]"
        git push origin main
    )
)

echo Concluido com sucesso!
