import os
import sys
import django
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGO_DIR = os.path.join(BASE_DIR, 'admin_panel')
sys.path.append(DJANGO_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from shop.models import Watch, Order, OrderItem, MessageHistory, BotUser
from carts_data import add_to_cart, get_cart_total, get_cart_items, clear_cart
import keyboards as kb

logger = logging.getLogger(__name__)


# ─── Утилита: сохранение истории сообщений ────────────────────────────────────

async def save_message(user_id: str, username: str, user_text: str, bot_reply: str):
    """Сохраняет диалог в БД"""
    try:
        await sync_to_async(MessageHistory.objects.create)(
            user_id=user_id,
            username=username or "",
            user_message=user_text[:500],
            bot_response=bot_reply[:500]
        )
    except Exception as e:
        logger.warning(f"Не удалось сохранить историю: {e}")


# ─── Утилита: сохранение пользователя ───────────────────────────────────────

async def save_user(user_id: str, username: str, first_name: str):
    """Сохраняет или обновляет пользователя в БД"""
    try:
        await sync_to_async(BotUser.objects.update_or_create)(
            user_id=user_id,
            defaults={
                "username": username or "",
                "first_name": first_name or ""
            }
        )
    except Exception as e:
        logger.warning(f"Не удалось сохранить пользователя: {e}")


# ─── /start ───────────────────────────────────────────────────────────────────

async def start_command(message: types.Message):
    user_name = message.from_user.first_name
    reply = (
        f"👋 Привет, {user_name}!\n"
        f"Добро пожаловать в магазин часов ⌚\n\n"
        f"📌 Доступные команды:\n"
        f"/start — главное меню\n"
        f"/help — помощь\n"
        f"/cart — моя корзина\n"
        f"/orders — мои заказы\n"
        f"/about — о магазине\n\n"
        f"Выбери категорию:"
    )
    await message.answer(reply, reply_markup=kb.get_category_keyboard())
    await save_message(
        str(message.from_user.id),
        message.from_user.username,
        "/start",
        reply
    )
    await save_user(
        str(message.from_user.id),
        message.from_user.username,
        message.from_user.first_name
    )


# ─── /help ────────────────────────────────────────────────────────────────────

async def help_command(message: types.Message):
    reply = (
        "❓ <b>Помощь по боту</b>\n\n"
        "Доступные команды:\n"
        "/start — главное меню\n"
        "/help — помощь\n"
        "/cart — моя корзина\n"
        "/orders — мои заказы\n"
        "/about — о магазине\n\n"
        "🔎 Что умеет бот:\n"
        "• Показывать каталог часов\n"
        "• Добавлять товары в корзину\n"
        "• Оформлять заказы\n"
        "• Показывать историю заказов\n\n"
        "Или просто нажимай кнопки в меню 👇"
    )
    await message.answer(reply, parse_mode="HTML", reply_markup=kb.get_category_keyboard())
    await save_message(str(message.from_user.id), message.from_user.username, "/help", reply)


# ─── /about ───────────────────────────────────────────────────────────────────

async def about_command(message: types.Message):
    reply = (
        "ℹ️ <b>О НАШЕМ МАГАЗИНЕ</b>\n\n"
        "Продаём качественные часы по доступным ценам 🇰🇿\n\n"
        "📦 Категории:\n"
        "  • Классические часы\n"
        "  • Смарт-часы\n\n"
        "💰 Цены от 18 900 ₸ до 159 900 ₸\n\n"
        "📞 По всем вопросам: @bboonah\n"
        "🕐 Работаем: 09:00 — 21:00 (пн-вс)"
    )
    await message.answer(reply, parse_mode="HTML", reply_markup=kb.get_back_keyboard())
    await save_message(str(message.from_user.id), message.from_user.username, "/about", reply)


# ─── /cart ────────────────────────────────────────────────────────────────────

async def cart_command(message: types.Message):
    user_id = str(message.from_user.id)
    cart_items = get_cart_items(user_id)

    if not cart_items:
        reply = "🛒 Корзина пуста!\n\nДобавьте часы из каталога"
        await message.answer(reply, reply_markup=kb.get_back_keyboard())
        await save_message(user_id, message.from_user.username, "/cart", reply)
        return

    text = "🛒 <b>ТВОЯ КОРЗИНА:</b>\n\n"
    for item in cart_items.values():
        item_total = item['price'] * item['quantity']
        text += f"⌚ {item['name']}\n"
        text += f"   {item['quantity']} x {item['price']} ₸ = {item_total} ₸\n\n"
    text += f"<b>ИТОГО: {get_cart_total(user_id)} ₸</b>"

    await message.answer(text, parse_mode="HTML", reply_markup=kb.get_cart_keyboard())
    await save_message(user_id, message.from_user.username, "/cart", text)


# ─── /orders ──────────────────────────────────────────────────────────────────

async def orders_command(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        orders = await sync_to_async(list)(
            Order.objects.filter(user_id=user_id).order_by('-created_at')[:5]
        )
    except Exception as e:
        logger.error(f"Ошибка получения заказов: {e}")
        reply = "⚠️ Не удалось загрузить заказы. Попробуйте позже."
        await message.answer(reply)
        await save_message(user_id, message.from_user.username, "/orders", reply)
        return

    if not orders:
        reply = "📦 У вас пока нет заказов.\n\nПерейдите в каталог и сделайте первый заказ!"
        await message.answer(reply, reply_markup=kb.get_back_keyboard())
        await save_message(user_id, message.from_user.username, "/orders", reply)
        return

    text = "📦 <b>Ваши последние заказы:</b>\n\n"
    for order in orders:
        text += f"🔖 Заказ №{order.id}\n"
        text += f"   Сумма: {order.total} ₸\n"
        text += f"   Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"   Статус: {order.status}\n\n"

    await message.answer(text, parse_mode="HTML", reply_markup=kb.get_back_keyboard())
    await save_message(user_id, message.from_user.username, "/orders", text)


# ─── /history — история диалога ───────────────────────────────────────────────

async def history_command(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        messages = await sync_to_async(list)(
            MessageHistory.objects.filter(user_id=user_id).order_by('-created_at')[:10]
        )
    except Exception as e:
        logger.error(f"Ошибка истории: {e}")
        await message.answer("⚠️ Не удалось загрузить историю.")
        return

    if not messages:
        await message.answer(
            "📜 История диалога пуста.",
            reply_markup=kb.get_back_keyboard()
        )
        return

    text = "📜 <b>Последние 10 сообщений:</b>\n\n"
    for msg in reversed(messages):
        text += f"🕐 {msg.created_at.strftime('%d.%m %H:%M')}\n"
        text += f"👤 Вы: {msg.user_message[:60]}\n"
        text += f"🤖 Бот: {msg.bot_response[:60]}\n\n"

    await message.answer(text, parse_mode="HTML", reply_markup=kb.get_back_keyboard())


# ─── Обработка любого текста ──────────────────────────────────────────────────

async def handle_text(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    text = message.text.strip() if message.text else ""

    # Пустой ввод
    if not text:
        reply = "⚠️ Пожалуйста, введите сообщение."
        await message.answer(reply, reply_markup=kb.get_category_keyboard())
        return

    text_lower = text.lower()
    reply = None

    # ── Приветствия
    if any(w in text_lower for w in ['привет', 'хай', 'hello', 'hi', 'здравствуй', 'салют', 'ку']):
        reply = (
            f"👋 Привет, {message.from_user.first_name}!\n"
            "Добро пожаловать в магазин часов ⌚\nВыбери что тебя интересует:"
        )
        await message.answer(reply, reply_markup=kb.get_category_keyboard())

    # ── Цены
    elif any(w in text_lower for w in ['цена', 'стоимость', 'сколько стоит', 'прайс', 'почём']):
        reply = "💰 Наши цены от 18 900 ₸ до 159 900 ₸\n\nСмотри каталог:"
        await message.answer(reply, reply_markup=kb.get_category_keyboard())

    # ── Каталог
    elif any(w in text_lower for w in ['каталог', 'товары', 'часы', 'ассортимент', 'что есть']):
        reply = "⌚ Вот наш каталог:"
        await message.answer(reply, reply_markup=kb.get_category_keyboard())

    # ── Корзина
    elif any(w in text_lower for w in ['корзина', 'cart', 'моя корзина']):
        await cart_command(message)
        return

    # ── Заказы
    elif any(w in text_lower for w in ['заказ', 'мои заказы', 'история заказов']):
        await orders_command(message)
        return

    # ── Помощь
    elif any(w in text_lower for w in ['помощь', 'help', 'что умеешь', 'команды']):
        await help_command(message)
        return

    # ── О магазине / Контакты
    elif any(w in text_lower for w in ['о магазине', 'контакт', 'связь', 'магазин', 'телефон', 'адрес']):
        reply = (
            "ℹ️ <b>О нашем магазине</b>\n\n"
            "Продаём качественные часы по доступным ценам.\n"
            "📞 По всем вопросам: @bboonah\n"
            "🕐 Работаем: 09:00 — 21:00\n"
            "💰 Цены в тенге 🇰🇿"
        )
        await message.answer(reply, parse_mode="HTML", reply_markup=kb.get_back_keyboard())

    # ── Доставка
    elif any(w in text_lower for w in ['доставка', 'привезут', 'доставят', 'курьер']):
        reply = (
            "🚚 <b>Доставка</b>\n\n"
            "• По Алматы — 1–2 рабочих дня\n"
            "• По Казахстану — 3–7 рабочих дней\n"
            "• Самовывоз — по договорённости\n\n"
            "Подробности: @bboonah"
        )
        await message.answer(reply, parse_mode="HTML", reply_markup=kb.get_back_keyboard())

    # ── Оплата
    elif any(w in text_lower for w in ['оплата', 'оплатить', 'платить', 'kaspi', 'каспи', 'перевод']):
        reply = (
            "💳 <b>Способы оплаты</b>\n\n"
            "• Kaspi Pay / Kaspi перевод\n"
            "• Наличные при получении\n"
            "• Перевод на карту\n\n"
            "Оформить заказ: /cart"
        )
        await message.answer(reply, parse_mode="HTML", reply_markup=kb.get_back_keyboard())

    # ── Гарантия
    elif any(w in text_lower for w in ['гарантия', 'гарант', 'возврат', 'брак']):
        reply = (
            "🛡 <b>Гарантия и возврат</b>\n\n"
            "• Гарантия на все часы: 12 месяцев\n"
            "• Возврат в течение 14 дней\n"
            "• При браке — замена или возврат средств\n\n"
            "Вопросы: @bboonah"
        )
        await message.answer(reply, parse_mode="HTML", reply_markup=kb.get_back_keyboard())

    # ── Классические часы
    elif any(w in text_lower for w in ['классик', 'классические', 'механические', 'аналог']):
        reply = "⌚ Классические часы — элегантность и стиль:"
        await message.answer(reply, reply_markup=kb.get_category_keyboard())

    # ── Смарт-часы
    elif any(w in text_lower for w in ['смарт', 'smart', 'умные', 'apple watch', 'samsung']):
        reply = "📱 Смарт-часы — технологии на запястье:"
        await message.answer(reply, reply_markup=kb.get_category_keyboard())

    # ── Спасибо
    elif any(w in text_lower for w in ['спасибо', 'благодар', 'thanks', 'thank you']):
        reply = "😊 Пожалуйста! Рады помочь!\n\nЕсли нужна помощь — пиши!"
        await message.answer(reply, reply_markup=kb.get_back_keyboard())

    # ── Пока / До свидания
    elif any(w in text_lower for w in ['пока', 'до свидания', 'bye', 'чао', 'бывай']):
        reply = "👋 До свидания! Ждём вас снова в магазине часов ⌚"
        await message.answer(reply, reply_markup=kb.get_back_keyboard())

    # ── Неизвестная команда
    else:
        reply = (
            f"🤔 Я не понял команду «{text[:50]}»\n\n"
            "Воспользуйся меню или введи /help для помощи."
        )
        await message.answer(reply, reply_markup=kb.get_category_keyboard())

    # Сохраняем в историю
    if reply:
        await save_message(user_id, username, text, reply)


# ─── Категории ────────────────────────────────────────────────────────────────

async def show_category(callback: types.CallbackQuery):
    category = callback.data

    try:
        watches = await sync_to_async(list)(
            Watch.objects.filter(category=category)
        )
    except Exception as e:
        logger.error(f"Ошибка загрузки категории: {e}")
        await callback.answer("⚠️ Ошибка загрузки товаров", show_alert=True)
        return

    if not watches:
        await callback.message.answer(
            "😔 В этой категории пока нет товаров",
            reply_markup=kb.get_back_keyboard()
        )
        await callback.answer()
        return

    await callback.message.answer(
        "Выбери модель:",
        reply_markup=kb.get_watches_keyboard(watches)
    )
    await callback.answer()


async def show_watches(callback: types.CallbackQuery):
    try:
        watches = await sync_to_async(list)(Watch.objects.all())
    except Exception as e:
        logger.error(f"Ошибка загрузки часов: {e}")
        await callback.answer("⚠️ Ошибка загрузки товаров", show_alert=True)
        return

    if not watches:
        await callback.message.answer(
            "😔 Пока товаров нет.",
            reply_markup=kb.get_back_keyboard()
        )
        await callback.answer()
        return

    await callback.message.answer(
        "⌚ Наши часы:\n\nВыбери модель:",
        reply_markup=kb.get_watches_keyboard(watches)
    )
    await callback.answer()


# ─── Карточка товара ──────────────────────────────────────────────────────────

async def show_one_watch(callback: types.CallbackQuery):
    watch_id = callback.data.replace('watch_', '')

    try:
        watch = await sync_to_async(Watch.objects.get)(id=watch_id)
    except Watch.DoesNotExist:
        await callback.answer("❌ Такого товара нет!", show_alert=True)
        return
    except Exception as e:
        logger.error(f"Ошибка загрузки товара {watch_id}: {e}")
        await callback.answer("⚠️ Ошибка загрузки товара", show_alert=True)
        return

    stock_text = f"{watch.in_stock} шт." if watch.in_stock > 0 else "❌ Нет в наличии"

    text = (
        f"⌚ <b>{watch.name}</b>\n"
        f"💰 Цена: {watch.price} ₸\n"
        f"📦 В наличии: {stock_text}\n\n"
        f"📝 Описание:\n{watch.description}\n\n"
        f"🏷 Бренд: {watch.brand}"
    )

    if watch.image_url:
        await callback.message.answer_photo(
            photo=watch.image_url,
            caption=text,
            parse_mode="HTML",
            reply_markup=kb.get_watch_keyboard(watch_id)
        )
    else:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=kb.get_watch_keyboard(watch_id)
        )
    await callback.answer()


# ─── Добавить в корзину ───────────────────────────────────────────────────────

async def buy_watch(callback: types.CallbackQuery):
    watch_id = callback.data.replace('buy_', '')

    try:
        watch = await sync_to_async(Watch.objects.get)(id=watch_id)
    except Watch.DoesNotExist:
        await callback.answer("❌ Такого товара нет!", show_alert=True)
        return
    except Exception as e:
        logger.error(f"Ошибка при добавлении в корзину: {e}")
        await callback.answer("⚠️ Ошибка. Попробуйте ещё раз", show_alert=True)
        return

    if watch.in_stock <= 0:
        await callback.answer("❌ Нет в наличии!", show_alert=True)
        return

    user_id = str(callback.from_user.id)
    watch_data = {'name': watch.name, 'price': watch.price, 'brand': watch.brand}
    quantity = add_to_cart(user_id, watch_id, watch_data)

    await callback.message.edit_caption(
        caption=f"✅ <b>{watch.name}</b>\n\nДобавлено в корзину: {quantity} шт.",
        parse_mode="HTML",
        reply_markup=kb.get_after_buy_keyboard()
    )
    await callback.answer("Добавлено в корзину!")


# ─── Корзина ──────────────────────────────────────────────────────────────────

async def show_cart(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    cart_items = get_cart_items(user_id)

    if not cart_items:
        await callback.message.edit_text(
            "🛒 Корзина пуста!\n\nДобавьте часы из каталога",
            reply_markup=kb.get_back_keyboard()
        )
        await callback.answer()
        return

    text = "🛒 <b>ТВОЯ КОРЗИНА:</b>\n\n"
    for item in cart_items.values():
        item_total = item['price'] * item['quantity']
        text += f"⌚ {item['name']}\n"
        text += f"   {item['quantity']} x {item['price']} ₸ = {item_total} ₸\n\n"
    text += f"<b>ИТОГО: {get_cart_total(user_id)} ₸</b>"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.get_cart_keyboard()
    )
    await callback.answer()


# ─── Оформление заказа ────────────────────────────────────────────────────────

async def checkout(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    total = get_cart_total(user_id)

    if total == 0:
        await callback.answer("❌ Корзина пуста!", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Подтвердить заказ', callback_data='confirm_order')],
        [InlineKeyboardButton(text='◀️ Назад', callback_data='show_cart')]
    ])

    await callback.message.edit_text(
        f"📋 <b>ОФОРМЛЕНИЕ ЗАКАЗА</b>\n\n"
        f"Сумма заказа: <b>{total} ₸</b>\n\n"
        f"Подтвердите заказ:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


async def confirm_order(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    cart_items = get_cart_items(user_id)
    total = get_cart_total(user_id)

    if not cart_items:
        await callback.answer("❌ Корзина пуста!", show_alert=True)
        return

    try:
        order = await sync_to_async(Order.objects.create)(
            user_id=user_id,
            username=callback.from_user.username or "",
            total=total,
            status="Принят"
        )
        for watch_id, item in cart_items.items():
            await sync_to_async(OrderItem.objects.create)(
                order=order,
                watch_id=watch_id,
                name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )
        order_id = order.id
    except Exception as e:
        logger.error(f"Ошибка сохранения заказа: {e}")
        order_id = "—"

    clear_cart(user_id)

    await callback.message.edit_text(
        f"✅ <b>ЗАКАЗ №{order_id} ПРИНЯТ!</b>\n\n"
        f"Сумма: {total} ₸\n\n"
        f"Спасибо за покупку! 🎉\n"
        f"Менеджер свяжется с вами в ближайшее время.",
        parse_mode="HTML",
        reply_markup=kb.get_back_keyboard()
    )
    await callback.answer()


async def clear_cart_handler(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    clear_cart(user_id)

    await callback.message.edit_text(
        "🗑 Корзина очищена!",
        reply_markup=kb.get_back_keyboard()
    )
    await callback.answer()


# ─── О магазине (callback) ────────────────────────────────────────────────────

async def about_shop(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ <b>О НАШЕМ МАГАЗИНЕ</b>\n\n"
        "Продаём качественные часы по доступным ценам 🇰🇿\n\n"
        "📦 Категории:\n"
        "  • Классические часы\n"
        "  • Смарт-часы\n\n"
        "💰 Цены от 18 900 ₸ до 159 900 ₸\n\n"
        "📞 По всем вопросам: @bboonah\n"
        "🕐 Работаем: 09:00 — 21:00 (пн-вс)\n"
        "💳 Оплата: Kaspi, наличные",
        parse_mode="HTML",
        reply_markup=kb.get_back_keyboard()
    )
    await callback.answer()


async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.answer(
        "Выбери категорию:",
        reply_markup=kb.get_category_keyboard()
    )
    await callback.answer()