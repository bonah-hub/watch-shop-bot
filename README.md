# ⌚ Watch Store Telegram Bot — Магазин Часов

Telegram-бот для продажи часов с каталогом, корзиной, оформлением заказов и веб-админкой. Реализован на Python с использованием aiogram и Django.

---

## 🛠 Используемые технологии

| Технология | Назначение |
|---|---|
| Python 3.10+ | Основной язык |
| aiogram 3.x | Telegram Bot API |
| Django 6.x | ORM и панель администратора |
| SQLite | База данных |
| aiohttp | Рассылка через Telegram API |
| asgiref | Асинхронный доступ к Django ORM |

---

## 📁 Структура проекта

```
watch_shop/
├── bot.py                  # Точка входа, регистрация хэндлеров
├── handlers.py             # Вся логика бота (команды + callback)
├── keyboards.py            # Inline-клавиатуры
├── carts_data.py           # Корзина (in-memory хранилище)
├── secret.py               # Токен Telegram бота
├── requirements.txt        # Зависимости
├── README.md               # Документация
└── admin_panel/            # Django-проект
    ├── manage.py
    ├── admin_panel/
    │   ├── settings.py
    │   └── urls.py
    └── shop/
        ├── models.py       # Watch, Order, OrderItem, MessageHistory, BotUser
        ├── admin.py        # Регистрация моделей в Admin
        ├── views.py        # Статистика и рассылка
        ├── urls.py         # Маршруты
        └── templates/
            └── shop/
                ├── statistics.html
                └── broadcast.html
```

---

## ⚙️ Установка

### 1. Клонируй репозиторий

```bash
git clone https://github.com/bonah-hub/watch-shop-bot.git
cd watch-shop-bot
```

### 2. Установи зависимости

```bash
pip install -r requirements.txt
```

### 3. Выполни миграции Django

```bash
cd admin_panel
python manage.py makemigrations
python manage.py migrate
```

### 4. Создай суперпользователя (для Django Admin)

```bash
python manage.py createsuperuser
```

### 5. Добавь токен бота в `secret.py`

```python
TOKEN = 'твой_токен_от_BotFather'
```

---

## 🚀 Запуск

Открой два терминала:

**Терминал 1 — Django:**
```bash
cd admin_panel
python manage.py runserver
```

**Терминал 2 — Бот:**
```bash
python bot.py
```

- Django Admin: `http://127.0.0.1:8000/admin/`
- Статистика: `http://127.0.0.1:8000/shop/statistics/`
- Рассылка: `http://127.0.0.1:8000/shop/broadcast/`

---

## 🤖 Команды бота

| Команда | Описание |
|---|---|
| `/start` | Главное меню |
| `/help` | Помощь и список команд |
| `/cart` | Моя корзина |
| `/orders` | История заказов |
| `/about` | О магазине |
| `/history` | История диалога |

---

## 💬 Текстовые запросы (15+)

| Ключевые слова | Ответ бота |
|---|---|
| привет, хай, hello | Приветствие |
| цена, стоимость, прайс | Диапазон цен |
| каталог, товары, часы | Открывает каталог |
| корзина, cart | Показывает корзину |
| заказ, мои заказы | История заказов |
| помощь, help | Список команд |
| доставка, курьер | Информация о доставке |
| оплата, kaspi, каспи | Способы оплаты |
| гарантия, возврат | Условия гарантии |
| о магазине, контакт | О магазине |
| классик, механические | Классические часы |
| смарт, умные | Смарт-часы |
| спасибо, thanks | Вежливый ответ |
| пока, bye | Прощание |
| неизвестное | Сообщение об ошибке |

---

## 🗃 База данных — модели Django

| Модель | Назначение |
|---|---|
| Watch | Товары (часы) |
| Order | Заказы пользователей |
| OrderItem | Позиции в заказе |
| MessageHistory | История диалогов с ботом |
| BotUser | Пользователи бота (для рассылки) |

---

## 🌐 Веб-панель администратора

- **Django Admin** — управление товарами, заказами, пользователями
- **Статистика** — количество пользователей, топ запросов, выручка
- **Рассылка** — отправка сообщений всем пользователям бота

---

## 🔒 Обработка ошибок

- ✅ Пустой ввод пользователя
- ✅ Неизвестная команда
- ✅ Товар не найден (DoesNotExist)
- ✅ Ошибка подключения к БД (try/except)
- ✅ Товар не в наличии
- ✅ Пустая корзина при оформлении
- ✅ Ошибка сохранения заказа

---

## 👤 Автор

- **Telegram:** @bboonah
- **GitHub:** https://github.com/bonah-hub/watch-shop-bot

---

## 📄 Лицензия

MIT
