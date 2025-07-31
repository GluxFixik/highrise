@echo off
title Highrise Bot 24/7
color 0A

echo ========================================
echo    Highrise Bot 24/7 Launcher
echo ========================================
echo.

echo Проверка зависимостей...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не установлен!
    echo Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo Python найден!
echo.

echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)

echo Зависимости установлены!
echo.

echo ========================================
echo Запуск бота в режиме 24/7...
echo Бот будет автоматически перезапускаться
echo при ошибках и работать непрерывно.
echo ========================================
echo.

echo Нажмите Ctrl+C для остановки
echo.

python run_forever.py

echo.
echo Бот остановлен.
pause 