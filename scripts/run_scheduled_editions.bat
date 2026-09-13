@echo off
setlocal
cd /d "C:\Users\mlori\toco\antigravity"

echo ======================================================
echo [%date% %time%] Executando Edicao Agendada (Fatos da Regiao)
echo ======================================================

"C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" run_fatos_da_regiao.py
"C:\Users\mlori\toco\antigravity\.venv\Scripts\python.exe" run_briefing.py

echo Enviando atualizacao para o GitHub / Vercel...
git add public/data/
git commit -m "chore(auto): nova edicao agendada publicada [skip ci]"
git push origin main

echo Concluido com sucesso!
