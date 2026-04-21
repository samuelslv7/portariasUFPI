@echo off
title Atualizador de Portarias - UFPI
echo ==========================================
echo    INICIANDO ATUALIZACAO DO SISTEMA
echo ==========================================
echo.

echo [1/2] Importando dados do Excel para o Banco...
python excel_to_sqlite.py
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao importar o Excel. Verifique se o arquivo contratos.xlsx esta aberto.
    pause
    exit /b
)

echo.
echo [2/2] Sincronizando links com o Google Drive...
python sync_drive.py
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha na sincronizacao com o Google Drive. Verifique sua internet.
    pause
    exit /b
)

echo.
echo ==========================================
echo    SUCESSO: TUDO ATUALIZADO!
echo ==========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul