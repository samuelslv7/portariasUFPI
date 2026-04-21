@echo off
title Atualizador de Portarias - UFPI
echo ==========================================
echo    INICIANDO ATUALIZACAO DO SISTEMA
echo ==========================================
echo.

:: 1. Processamento de Dados
echo [1/3] Importando dados do Excel para o Banco...
python atualizarBD.py
if %errorlevel% neq 0 goto :erro_excel

echo.
echo [2/3] Sincronizando links com o Google Drive...
python sync_drive.py
if %errorlevel% neq 0 goto :erro_drive

:: 2. Envio para o GitHub (Vercel)
echo.
echo [3/3] Enviando atualizacoes para o servidor (GitHub)...
git add db/contratos_ufpi.db
git commit -m "Atualizacao de dados: %date% %time%"
git push origin main

if %errorlevel% neq 0 goto :erro_git

echo.
echo ==========================================
echo    SUCESSO: SITE ATUALIZADO NA VERCEL!
echo ==========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
exit

:erro_excel
echo.
echo ERRO: Falha ao importar o Excel. Verifique se o arquivo contratos.xlsx esta aberto.
pause
exit

:erro_drive
echo.
echo ERRO: Falha na sincronizacao com o Google Drive. Verifique a internet.
pause
exit

:erro_git
echo.
echo ERRO: Falha ao enviar para o GitHub. 
echo Verifique se o Git esta instalado e se voce tem permissao de acesso.
pause
exit