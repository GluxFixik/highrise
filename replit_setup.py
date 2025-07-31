#!/usr/bin/env python3
"""
Специальный файл для запуска бота в Replit
Автоматически настраивает переменные окружения
"""

import os
import sys
import asyncio
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_replit():
    """Настройка переменных окружения для Replit"""
    
    # Проверяем, есть ли переменные окружения
    room_id = os.environ.get('ROOM_ID')
    api_token = os.environ.get('API_TOKEN')
    
    if not room_id or not api_token:
        print("⚠️ Переменные окружения не найдены!")
        print("Настройте Secrets в Replit:")
        print("1. Нажмите Tools → Secrets")
        print("2. Добавьте ROOM_ID = ваш_id_комнаты")
        print("3. Добавьте API_TOKEN = ваш_api_токен")
        print("4. Перезапустите Repl")
        return False
    
    print("✅ Переменные окружения настроены!")
    print(f"Room ID: {room_id}")
    print(f"API Token: {api_token[:10]}...")
    return True

async def run_bot_replit():
    """Запуск бота в Replit"""
    
    if not setup_replit():
        return
    
    try:
        from main import run_bot
        
        print("🚀 Запуск бота в Replit...")
        print("=" * 50)
        
        room_id = os.environ.get('ROOM_ID')
        api_token = os.environ.get('API_TOKEN')
        
        await run_bot(room_id, api_token)
        
    except KeyboardInterrupt:
        print("\n⚠️ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("Попробуйте перезапустить Repl")

if __name__ == "__main__":
    print("🎯 Highrise Bot для Replit")
    print("=" * 30)
    
    try:
        asyncio.run(run_bot_replit())
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        print("Проверьте настройки и попробуйте снова") 