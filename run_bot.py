#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from main import Bot

async def main():
    """Основная функция запуска бота"""
    print("=" * 50)
    print("Запуск Highrise бота")
    print("=" * 50)
    
    try:
        # Загружаем конфигурацию
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"Подключение к комнате: {config['room_id']}")
        print("Бот запущен. Нажмите Ctrl+C для остановки.")
        
        # Создаем и запускаем бота
        bot = Bot()
        
        # Здесь должен быть код для подключения к Highrise
        # Но пока просто ждем
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    asyncio.run(main()) 