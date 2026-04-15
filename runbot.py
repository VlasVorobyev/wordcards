#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Запуск Telegram-бота для квиза.
Команда: python run_bot.py
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Запускаем бота
from bot.bot import main

if __name__ == '__main__':
    print("🚀 Запуск бота...")
    print("⚠️ Убедитесь, что Django сервер запущен (python manage.py runserver)")
    print("=" * 50)
    main()
