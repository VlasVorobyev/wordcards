#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram-бот для квиза.
Позволяет проверять знание слов в формате вопрос-ответ.
"""

import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordcards.settings')

import django

django.setup()

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from bot.utils import get_random_card, get_stats

# --- Конфигурация ---

TOKEN = "7787469948:AAE2L2dHhO5Lyggbph94kGeTSFv4QXlgMyE"


# --- Клавиатуры ---
def get_main_keyboard():
    """Главная клавиатура."""
    keyboard = [
        [KeyboardButton("🎯 Начать квиз")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_quiz_keyboard():
    """Клавиатура во время квиза."""
    keyboard = [
        [KeyboardButton("🎲 Новое слово")],
        [KeyboardButton("🏠 В главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- Обработчики команд ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user

    # Очищаем состояние квиза
    context.user_data.clear()

    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"🎯 **WordCards Quiz Bot**\n\n"
        f"Я помогу проверить твои знания английских слов!\n\n"
        f"📖 **Как играть:**\n"
        f"1. Нажми «Начать квиз»\n"
        f"2. Я покажу слово на английском\n"
        f"3. Напиши перевод в чат\n"
        f"4. Узнай правильный ответ!\n\n"
        f"🚀 Нажми «Начать квиз» или отправь команду /quiz",
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    await update.message.reply_text(
        "📖 **Помощь по боту**\n\n"
        "🎯 **/quiz** или «Начать квиз» - начать проверку знаний\n"
        "📊 **/stats** или «Статистика» - посмотреть прогресс\n"
        "🏠 **/start** - главное меню\n"
        "❓ **/help** - эта справка\n\n"
        "**Как отвечать:**\n"
        "Просто напиши перевод слова в чат.\n"
        "Бот сразу скажет, правильно или нет!\n\n"
        "Пример:\n"
        "Бот: *cat*\n"
        "Ты: кошка\n"
        "Бот: ✅ Правильно!",
        parse_mode='Markdown'
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику."""
    stats_data = await get_stats()

    if stats_data['total'] == 0:
        await update.message.reply_text(
            "📭 **В базе пока нет слов!**\n\n"
            "Добавьте слова через веб-интерфейс или админку Django,\n"
            "и возвращайтесь играть в квиз! 🎯",
            parse_mode='Markdown'
        )
    else:
        message = (
            f"📊 **Статистика ваших слов**\n\n"
            f"📖 Всего слов: *{stats_data['total']}*\n"
            f"✅ С примерами: *{stats_data['with_examples']}*\n"
            f"📝 Без примеров: *{stats_data['without_examples']}*\n\n"
            f"🎯 Готов проверить знания? Нажми /quiz!"
        )
        await update.message.reply_text(message, parse_mode='Markdown')


async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать квиз."""
    card = await get_random_card()

    if not card:
        await update.message.reply_text(
            "❌ **Нет карточек для квиза!**\n\n"
            "Сначала добавьте слова через веб-интерфейс:\n"
            "http://127.0.0.1:8000/create/\n\n"
            "После добавления слов возвращайтесь! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return

    # Сохраняем текущее слово в контексте
    context.user_data['current_word'] = card.word
    context.user_data['current_translation'] = card.translation
    context.user_data['current_example'] = card.example

    message = (
        f"🎯 **Квиз начался!**\n\n"
        f"📖 **Переведи слово:**\n"
        f"🔤 *{card.word}*\n\n"
        f"✏️ Напиши перевод в чат:"
    )

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_quiz_keyboard()
    )


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверить ответ пользователя."""
    user_answer = update.message.text.strip()

    # Проверяем, есть ли активный квиз
    if 'current_word' not in context.user_data:
        await update.message.reply_text(
            "🎯 Сначала начни квиз командой /quiz или нажми «Начать квиз»!",
            reply_markup=get_main_keyboard()
        )
        return

    current_word = context.user_data['current_word']
    correct_translation = context.user_data['current_translation']
    example = context.user_data.get('current_example', '')

    # Проверяем ответ
    if user_answer.lower().strip() == correct_translation.lower():
        response = (
            f"✅ **Правильно!** 🎉\n\n"
            f"📖 *{current_word}* → *{correct_translation}*\n"
        )
        if example:
            response += f"💬 Пример: _{example}_\n"
        response += f"\nПродолжай в том же духе! Нажми «Новое слово»"
    else:
        response = (
            f"❌ **Неправильно!**\n\n"
            f"📖 *{current_word}*\n"
            f"✅ Правильный перевод: *{correct_translation}*\n"
            f"❌ Твой ответ: *{user_answer}*\n"
        )
        if example:
            response += f"💬 Пример использования: _{example}_\n"
        response += f"\nЗапомни и попробуй следующее слово!"

    # Очищаем текущее слово, чтобы пользователь нажал "Новое слово"
    del context.user_data['current_word']
    del context.user_data['current_translation']
    if 'current_example' in context.user_data:
        del context.user_data['current_example']

    await update.message.reply_text(
        response,
        parse_mode='Markdown',
        reply_markup=get_quiz_keyboard()
    )


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать новое слово."""
    await quiz_start(update, context)


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться в главное меню."""
    context.user_data.clear()
    await update.message.reply_text(
        "🏠 **Возвращаемся в главное меню**\n\n"
        "Когда будешь готов - нажми «Начать квиз»!",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (не команд)."""
    text = update.message.text

    # Обработка кнопок
    if text == "🎯 Начать квиз":
        await quiz_start(update, context)
    elif text == "📊 Статистика":
        await stats(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)
    elif text == "🎲 Новое слово":
        await new_word(update, context)
    elif text == "🏠 В главное меню":
        await back_to_menu(update, context)
    else:
        # Если это не кнопка - проверяем как ответ на квиз
        await check_answer(update, context)


# --- Обработчик ошибок ---
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок."""
    print(f"❌ Ошибка: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😵 Произошла ошибка. Пожалуйста, попробуйте еще раз или начните заново с /start"
        )


# --- Запуск бота ---
def main():
    """Запуск Telegram-бота."""
    print("🤖 Запуск WordCards Quiz Bot...")
    print("📖 Бот для проверки знаний английских слов")
    print("=" * 40)

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quiz", quiz_start))
    application.add_handler(CommandHandler("stats", stats))

    # Обработчик для всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    print("✅ Бот успешно запущен!")
    print("💬 Откройте Telegram и найдите своего бота")
    print("=" * 40)

    application.run_polling()


if __name__ == '__main__':
    main()
