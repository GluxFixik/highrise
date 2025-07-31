#!/usr/bin/env python3
"""
Скрипт для непрерывной работы бота 24/7
Автоматически перезапускает бота при ошибках
"""

import asyncio
import sys
import time
import traceback
from datetime import datetime
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import run_bot, load_config

def log_message(message: str):
    """Логирование сообщений"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Выводим в консоль
    print(log_entry.strip())
    
    # Записываем в файл
    with open("bot_24_7.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

async def run_bot_with_restart():
    """Запускает бота с автоматическим перезапуском"""
    restart_count = 0
    max_restarts = 1000  # Максимальное количество перезапусков
    
    while restart_count < max_restarts:
        try:
            log_message(f"🚀 Запуск бота (попытка {restart_count + 1})")
            
            # Загружаем конфигурацию или берем из переменных окружения
            room_id = os.environ.get('ROOM_ID')
            api_key = os.environ.get('API_TOKEN')
            
            if not room_id or not api_key:
                config = load_config()
                room_id = config.get("room_id", "668bc58d2aa6dd7d3bc16037")
                api_key = config.get("bot_token", "0288f3080eaaf24ce8748445f623737bebbbea63db35fbbd8ec0371ffc5840f6")
            
            log_message(f"📡 Подключение к комнате: {room_id}")
            
            # Запускаем бота
            await run_bot(room_id, api_key)
            
        except KeyboardInterrupt:
            log_message("⚠️ Бот остановлен пользователем")
            break
            
        except Exception as e:
            restart_count += 1
            error_msg = f"❌ Ошибка бота (попытка {restart_count}): {str(e)}"
            log_message(error_msg)
            
            # Логируем полную ошибку
            with open("bot_errors.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now()}] Ошибка бота:\n")
                f.write(traceback.format_exc())
                f.write("\n" + "="*50 + "\n")
            
            # Ждем перед перезапуском
            wait_time = min(30, restart_count * 5)  # Увеличиваем время ожидания
            log_message(f"⏳ Ожидание {wait_time} секунд перед перезапуском...")
            time.sleep(wait_time)
            
        except asyncio.CancelledError:
            log_message("⚠️ Бот отменен")
            break
    
    if restart_count >= max_restarts:
        log_message("❌ Достигнуто максимальное количество перезапусков. Бот остановлен.")

if __name__ == "__main__":
    log_message("🎯 Запуск системы 24/7 для Highrise бота")
    log_message("=" * 50)
    
    try:
        # Запускаем бесконечный цикл
        asyncio.run(run_bot_with_restart())
    except KeyboardInterrupt:
        log_message("🛑 Система 24/7 остановлена пользователем")
    except Exception as e:
        log_message(f"💥 Критическая ошибка системы: {e}")
        with open("bot_errors.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] Критическая ошибка системы:\n")
            f.write(traceback.format_exc())
    
    log_message("👋 Система 24/7 завершена") 