@echo off
setlocal
cd /d "C:\Users\mlori\toco\antigravity"

echo ======================================================
echo [%date% %time%] Executando Edicao Agendada (Fatos da Regiao)
echo ======================================================

echo Sincronizando com o GitHub...
git pull --rebase origin main

"C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" run_fatos_da_regiao.py

echo Enviando atualizacao para o GitHub / Vercel...
git pull --rebase origin main
git add public/data/ reports/
git diff --staged --quiet || (
    git commit -m "chore(auto): nova edicao agendada publicada [skip ci]"
    git push origin main
)

echo Concluido com sucesso!
