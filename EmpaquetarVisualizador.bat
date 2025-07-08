@echo off
title 🎁 Empaquetando Visualizador ICA...
cd /d %~dp0

echo 🔄 Cerrando procesos anteriores...
taskkill /f /im VisualizadorICA.exe >nul 2>&1

echo 🔄 Limpiando versiones anteriores...
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1

echo 🚀 Activando entorno virtual...
call venv\Scripts\activate

echo 🛠️ Compilando con PyInstaller...
pyinstaller --noconfirm app.spec

if exist dist\VisualizadorICA\VisualizadorICA.exe (
    echo ✅ ¡Empaquetado completo!
    start dist\VisualizadorICA\VisualizadorICA.exe
) else (
    echo ❌ Error: el archivo ejecutable no se generó.
)

pause
