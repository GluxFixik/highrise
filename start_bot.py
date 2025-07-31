#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json

def check_dependencies():
    """Проверяет зависимости"""
    print("Проверка зависимостей...")
    try:
        import highrise
        print("✓ Highrise установлен")
    except ImportError:
        print("✗ Highrise не установлен. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "highrise"])
        print("✓ Highrise установлен")

def check_config():
    """Проверяет конфигурацию"""
    print("Проверка конфигурации...")
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        if not config.get("bot_token"):
            print("✗ Bot token не найден в config.json")
            return False
        
        if not config.get("room_id"):
            print("✗ Room ID не найден в config.json")
            return False
        
        print("✓ Конфигурация корректна")
        return True
        
    except FileNotFoundError:
        print("✗ Файл config.json не найден")
        return False
    except json.JSONDecodeError:
        print("✗ Ошибка в формате config.json")
        return False

def main():
    """Основная функция"""
    print("=" * 50)
    print("Запуск Highrise бота")
    print("=" * 50)
    
    # Проверяем зависимости
    check_dependencies()
    
    # Проверяем конфигурацию
    if not check_config():
        print("\nОшибка: Проверьте config.json и API токен")
        input("Нажмите Enter для выхода...")
        return
    
    print("\nЗапуск бота...")
    try:
        # Загружаем конфигурацию
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Запускаем бота через highrise
        subprocess.run([sys.executable, "-m", "highrise", "run", "main:Bot", config["room_id"], config["bot_token"]], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nОшибка запуска бота: {e}")
        input("Нажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 