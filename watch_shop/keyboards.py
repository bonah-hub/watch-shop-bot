from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Классические часы', callback_data='classic')],
        [InlineKeyboardButton(text='Смарт-часы', callback_data='smart')],
        [InlineKeyboardButton(text='Моя корзина', callback_data='show_cart')],
        [InlineKeyboardButton(text='О магазине', callback_data='about')]
    ])


def get_watches_keyboard(watches):
    buttons = []

    for watch in watches:
        buttons.append([
            InlineKeyboardButton(
                text=f"{watch.name} - {watch.price} ₸",
                callback_data=f'watch_{watch.id}'
            )
        ])

    buttons.append([
        InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_watch_keyboard(watch_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Купить', callback_data=f'buy_{watch_id}'),
            InlineKeyboardButton(text='Назад', callback_data='show_watches')
        ]
    ])


def get_after_buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='В корзину', callback_data='show_cart')],
        [InlineKeyboardButton(text='Еще часы', callback_data='show_watches')],
        [InlineKeyboardButton(text='В меню', callback_data='back_to_menu')]
    ])


def get_cart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Оформить заказ', callback_data='checkout')],
        [InlineKeyboardButton(text='Очистить корзину', callback_data='clear_cart')],
        [InlineKeyboardButton(text='Еще часы', callback_data='show_watches')]
    ])


def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='В меню', callback_data='back_to_menu')]
    ])