#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем бота
if __name__ == "__main__":
    # Запускаем через highrise модуль
    os.system(f"{sys.executable} -m highrise run main:Bot 64bc45f302dd5ba15222881e ff1bbf06677761de16e693e46463b528e41f0562664fa82b1377016575604352") 