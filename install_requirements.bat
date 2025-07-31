@echo off
chcp 65001 >nul
title Highrise Bot - Установка зависимостей

echo ================================================
echo    Установка зависимостей для Highrise бота
echo ================================================

cd /d "%~dp0"

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

echo.
echo Установка Highrise...
pip install highrise-bot-sdk

echo.
echo Установка дополнительных зависимостей...
pip install asyncio

echo.
echo ================================================
echo Установка завершена!
echo Теперь можете запустить бота через start_bot_alternative.bat
echo ================================================
pause 