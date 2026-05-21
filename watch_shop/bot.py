import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import secret
from handlers import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=secret.TOKEN)
dp = Dispatcher()

# ── Команды
dp.message.register(start_command, Command("start"))
dp.message.register(help_command, Command("help"))
dp.message.register(cart_command, Command("cart"))
dp.message.register(orders_command, Command("orders"))
dp.message.register(about_command, Command("about"))
dp.message.register(history_command, Command("history"))

# ── Callback кнопки
dp.callback_query.register(show_category, lambda c: c.data in ['classic', 'smart'])
dp.callback_query.register(show_watches, lambda c: c.data == 'show_watches')
dp.callback_query.register(show_one_watch, lambda c: c.data.startswith('watch_'))
dp.callback_query.register(buy_watch, lambda c: c.data.startswith('buy_'))
dp.callback_query.register(show_cart, lambda c: c.data == 'show_cart')
dp.callback_query.register(checkout, lambda c: c.data == 'checkout')
dp.callback_query.register(confirm_order, lambda c: c.data == 'confirm_order')
dp.callback_query.register(clear_cart_handler, lambda c: c.data == 'clear_cart')
dp.callback_query.register(about_shop, lambda c: c.data == 'about')
dp.callback_query.register(back_to_menu, lambda c: c.data == 'back_to_menu')

# ── Любой текст — в конце
dp.message.register(handle_text)


async def main():
    print("=" * 50)
    print("⌚ МАГАЗИН ЧАСОВ ЗАПУЩЕН")
    print("Цены в тенге 🇰🇿")
    print("=" * 50)

    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())