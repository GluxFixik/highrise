@echo off
chcp 65001 >nul
title Highrise Bot

echo ================================================
echo           Запуск Highrise бота
echo ================================================

cd /d "%~dp0"

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден!
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
echo Установка переменных окружения...
set ROOM_ID=64bc45f302dd5ba15222881e
set API_TOKEN=40b0d4006bd11104047ed0284b8a16deb9756d699744fcfaa00760dd492503edf

echo Room ID: %ROOM_ID%
echo API Token: %API_TOKEN:~0,10%...

echo.
echo Запуск бота...
python -m highrise run main:Bot

if errorlevel 1 (
    echo.
    echo Ошибка запуска бота!
    echo Возможно, изменился синтаксис команды
    pause
) else (
    echo.
    echo Бот остановлен
    pause
) 