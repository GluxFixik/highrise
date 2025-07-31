#!/usr/bin/env python3
"""
Простой тест для Render
"""

import os
import sys
import json
from datetime import datetime

def test_imports():
    """Тестируем импорты"""
    try:
        import asyncio
        print("✅ asyncio импортирован успешно")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта asyncio: {e}")
        return False

def test_config():
    """Тестируем конфигурацию"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ['bot_token', 'room_id', 'admin_ids', 'owner_id']
        for field in required_fields:
            if field not in config:
                print(f"❌ Отсутствует поле: {field}")
                return False
        
        print("✅ Конфигурация загружена успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_main_import():
    """Тестируем импорт main.py"""
    try:
        from main import run_bot, load_config
        print("✅ main.py импортирован успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта main.py: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование развертывания на Render")
    print("=" * 50)
    
    # Тест 1: Импорты
    test1 = test_imports()
    
    # Тест 2: Конфигурация
    test2 = test_config()
    
    # Тест 3: Основной модуль
    test3 = test_main_import()
    
    print("=" * 50)
    if all([test1, test2, test3]):
        print("✅ Все тесты пройдены! Развертывание готово.")
        return 0
    else:
        print("❌ Некоторые тесты не пройдены.")
        return 1

if __name__ == "__main__":
    exit(main()) 