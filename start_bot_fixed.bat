@echo off
chcp 65001 >nul
title Highrise Bot Launcher

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

echo Проверка зависимостей...
python -c "import highrise" >nul 2>&1
if errorlevel 1 (
    echo Установка Highrise...
    pip install highrise
)

echo.
echo Запуск бота...

REM Попробуем разные варианты запуска
echo Попытка 1: Стандартный запуск
python -m highrise run main:Bot 64bc45f302dd5ba15222881e 40b0d4006bd11104047ed0284b8a16deb9756d699744fcfaa00760dd492503edf

if errorlevel 1 (
    echo.
    echo Попытка 2: Запуск с переменными окружения
    set ROOM_ID=64bc45f302dd5ba15222881e
    set API_TOKEN=40b0d4006bd11104047ed0284b8a16deb9756d699744fcfaa00760dd492503edf
    python -m highrise run main:Bot
)

if errorlevel 1 (
    echo.
    echo Попытка 3: Запуск через Python скрипт
    python -c "import os; os.environ['ROOM_ID']='64bc45f302dd5ba15222881e'; os.environ['API_TOKEN']='40b0d4006bd11104047ed0284b8a16deb9756d699744fcfaa00760dd492503edf'; import subprocess; subprocess.run(['python', '-m', 'highrise', 'run', 'main:Bot'])"
)

if errorlevel 1 (
    echo.
    echo Ошибка запуска бота!
    echo Проверьте config.json и API токен
    echo Возможно, изменился синтаксис команды highrise
    pause
) else (
    echo.
    echo Бот остановлен
    pause
) 