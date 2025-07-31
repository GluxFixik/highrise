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
python -m highrise run main:Bot 64bc45f302dd5ba15222881e 40b0d4006bd11104047ed0284b8a16deb9756d699744fcfaa00760dd492503edf

if errorlevel 1 (
    echo.
    echo Ошибка запуска бота!
    echo Проверьте config.json и API токен
    pause
) else (
    echo.
    echo Бот остановлен
    pause
) 