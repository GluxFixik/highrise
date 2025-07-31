#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def main():
    """Запуск бота с переменными окружения"""
    print("=" * 50)
    print("Запуск Highrise бота")
    print("=" * 50)
    
    # Устанавливаем переменные окружения
    os.environ['ROOM_ID'] = '64bc45f302dd5ba15222881e'
    os.environ['API_TOKEN'] = '40b0d4006bd11104047ed0284b8a16deb9756d699744fcfaa00760dd492503edf'
    
    print(f"Room ID: {os.environ['ROOM_ID']}")
    print(f"API Token: {os.environ['API_TOKEN'][:10]}...")
    print()
    
    try:
        # Запускаем бота
        result = subprocess.run([
            sys.executable, 
            '-m', 
            'highrise', 
            'run', 
            'main:Bot'
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска бота: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 