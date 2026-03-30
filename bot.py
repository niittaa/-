import logging
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # Токен из переменных Bothost

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📱 О приложении", callback_data='about')],
        [InlineKeyboardButton("✨ Как добавлять заметки", callback_data='add')],
        [InlineKeyboardButton("⭐ Оценка звездами", callback_data='rating')],
        [InlineKeyboardButton("💡 Примеры", callback_data='examples')],
        [InlineKeyboardButton("❓ Задать вопрос", callback_data='ask')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '🤖 Добро пожаловать в консультант по приложению **Bookmaze**!\n\n'
        'Это приложение для записи заметок к прочитанным книгам:\n'
        '📖 Название + автор\n'
        '⭐ Оценка 1-5 звезд\n'
        '📝 Ваши мысли и цитаты\n\n'
        'Выберите тему или задайте вопрос!',
        reply_markup=reply_markup, parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'about':
        await query.edit_message_text(
            '📱 **О приложении Bookmaze**\n\n'
            '**Основные функции:**\n'
            '• Добавление книг с заметками\n'
            '• Оценка 1-5 ⭐\n'
            '• Поиск по названию/автору\n'
            '• Категории (фантастика, классика...)\n'
            '**Сохранение:** Локально + облако (Google Drive)\n\n'
            '/start - меню',
            parse_mode='Markdown'
        )
    elif query.data == 'add':
        await query.edit_message_text(
            '✨ **Как добавлять заметки**\n\n'
            '1. Нажмите **"Добавить книгу"**\n'
            '2. Заполните поля:\n'
            '   📖 **Название** (обязательно)\n'
            '   ✍️ **Автор**\n'
            '   ⭐ **Оценка** (1-5 звезд)\n'
            '   📝 **Заметка** (ваши мысли)\n'
            '3. **Сохранить**\n\n'
            'Заметка появится в списке!',
            parse_mode='Markdown'
        )
    elif query.data == 'rating':
        await query.edit_message_text(
            '⭐ **Система оценок**\n\n'
            '• 1⭐ - Не понравилось\n'
            '• 2⭐ - Плохо\n'
            '• 3⭐ - Нормально\n'
            '• 4⭐ - Хорошо\n'
            '• 5⭐ - Шедевр!\n\n'
            '**Визуально:** Градиент звездочек\n'
            'Средний рейтинг по авторам автоматически!',
            parse_mode='Markdown'
        )
    elif query.data == 'examples':
        await query.edit_message_text(
            '💡 **Примеры заметок**\n\n'
            '**Книга:** "1984"\n'
            '**Автор:** Джордж Оруэлл\n'
            '**Оценка:** 5⭐\n'
            '**Заметка:** "Большой Брат смотрит. Классика дистопии."\n\n'
            '**Книга:** "Мастер и Маргарита"\n'
            '**Автор:** Михаил Булгаков\n'
            '**Оценка:** 4⭐\n'
            '**Заметка:** "Сатира + мистика + любовь. Понравилось!"\n\n'
            'Заметки можно редактировать.',
            parse_mode='Markdown'
        )
    elif query.data == 'ask':
        await query.edit_message_text(
            '❓ **Задайте вопрос**\n\n'
            'Напишите в чат любой вопрос о приложении:\n'
            '• "Как искать книги?"\n'
            '• "Можно ли делиться заметками?"\n'
            '• "Есть ли статистика?"\n\n'
            'Я отвечу подробно! 👇'
        )
        context.user_data['mode'] = 'question'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()

    if context.user_data.get('mode') == 'question':
        response = await get_smart_response(text)
        await update.message.reply_text(response, parse_mode='Markdown')
        context.user_data.pop('mode', None)
    else:
        if any(word in text for word in ['как добавить', 'добавлять', 'создать']):
            await update.message.reply_text(
                '✨ **Добавление заметки:**\n'
                '1. "Добавить книгу"\n'
                '2. Название | Автор | 1-5 | Заметка\n'
                '3. Сохранить!\n\n'
                '/start - полное меню',
                parse_mode='Markdown'
            )
        elif any(word in text for word in ['оценка', 'звезды', 'рейтинг']):
            await update.message.reply_text(
                '⭐ **Оценка:** Выбирайте 1-5 звезд.\n'
                'Автоматическая статистика по авторам!',
                parse_mode='Markdown'
            )
        elif 'поиск' in text:
            await update.message.reply_text(
                '🔍 **Поиск:** По названию, автору, тегам.\n'
                'Фильтры: по оценке, дате чтения.',
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                'Информация по Bookmaze!\n'
                'Выберите кнопку или /start.\n'
                'Задайте вопрос текстом.',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Меню", callback_data='start')]])
            )

async def get_smart_response(question: str) -> str:
    if 'статистика' in question or 'аналитика' in question:
        return '📊 **Статистика:**\n• Книг прочитано\n• Средний рейтинг\n• Топ-авторы\n• Рейтинг по жанрам'
    elif 'делиться' in question or 'экспорт' in question:
        return '📤 **Поделиться:**\n• Экспорт PDF/CSV\n• Ссылка на заметку\n• Импорт из Goodreads'
    elif 'удалить' in question:
        return '🗑️ **Удаление:**\nДолгое нажатие на заметку → Удалить\nАрхив вместо удаления'
    elif 'синхронизация' in question or 'облако' in question:
        return '☁️ **Синхронизация:**\n• Google Drive\n• Автосохранение\n• Мультиустройства'
    else:
        return '💡 Хороший вопрос! В BookNotes есть поиск, статистика, экспорт. Уточните?'

def main():
    print("🚀 Консультант Bookmaze запущен!")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
