@echo off
chcp 65001 >nul
title Highrise Bot - Финальная версия

echo ================================================
echo           Запуск Highrise бота
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

echo Проверка Highrise...
python -c "import highrise" >nul 2>&1
if errorlevel 1 (
    echo Установка Highrise...
    pip install highrise
)

echo.
echo Запуск бота...
echo Нажмите Ctrl+C для остановки
echo.

:loop
python main.py
echo.
echo Бот остановлен. Перезапуск через 5 секунд...
timeout /t 5 /nobreak >nul
goto loop 