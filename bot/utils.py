"""
Вспомогательные функции для Telegram-бота (только квиз).
С использованием sync_to_async для асинхронной работы с Django ORM.
"""

import os
import sys
import random

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linguacards.settings')

import django
django.setup()

from asgiref.sync import sync_to_async
from cards.models import Card


@sync_to_async
def get_random_card():
    """Возвращает случайную карточку из базы (асинхронно)."""
    cards = list(Card.objects.all())
    if not cards:
        return None
    return random.choice(cards)


@sync_to_async
def get_stats():
    """Возвращает статистику по карточкам (асинхронно)."""
    total = Card.objects.count()
    with_examples = Card.objects.exclude(example='').count()
    return {
        'total': total,
        'with_examples': with_examples,
        'without_examples': total - with_examples,
    }


@sync_to_async
def check_translation(word, user_answer):
    """Проверяет правильность перевода (асинхронно)."""
    try:
        card = Card.objects.get(word__iexact=word)
        return user_answer.lower().strip() == card.translation.lower(), card.translation, card.example
    except Card.DoesNotExist:
        return False, None, None
