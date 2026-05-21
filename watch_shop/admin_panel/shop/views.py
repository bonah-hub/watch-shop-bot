from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from .models import Order, MessageHistory, BotUser
import asyncio
import aiohttp
import os
import sys

# Путь к secret.py — он лежит на уровень выше admin_panel/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

try:
    import secret
    BOT_TOKEN = secret.TOKEN
except ImportError:
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')


# ─── Статистика ───────────────────────────────────────────────────────────────

@staff_member_required
def statistics(request):
    total_users = BotUser.objects.count()
    total_messages = MessageHistory.objects.count()
    total_orders = Order.objects.count()
    total_revenue = sum(o.total for o in Order.objects.all())

    top_commands = (
        MessageHistory.objects
        .values('user_message')
        .annotate(count=Count('user_message'))
        .order_by('-count')[:5]
    )

    recent_users = BotUser.objects.order_by('-created_at')[:10]

    orders_by_status = (
        Order.objects
        .values('status')
        .annotate(count=Count('status'))
        .order_by('-count')
    )

    context = {
        'total_users': total_users,
        'total_messages': total_messages,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'top_commands': top_commands,
        'recent_users': recent_users,
        'orders_by_status': orders_by_status,
    }
    return render(request, 'shop/statistics.html', context)


# ─── Рассылка ─────────────────────────────────────────────────────────────────

@staff_member_required
def broadcast(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text:
            messages.error(request, '❌ Введите текст сообщения!')
            return redirect('shop:broadcast')

        users = list(BotUser.objects.values_list('user_id', flat=True))
        if not users:
            messages.error(request, '❌ Нет пользователей для рассылки!')
            return redirect('shop:broadcast')

        sent, failed = asyncio.run(_send_broadcast(users, text))
        messages.success(
            request,
            f'✅ Рассылка завершена! Отправлено: {sent}, Ошибок: {failed}'
        )
        return redirect('shop:broadcast')

    total_users = BotUser.objects.count()
    return render(request, 'shop/broadcast.html', {'total_users': total_users})


async def _send_broadcast(user_ids: list, text: str):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    sent = 0
    failed = 0

    async with aiohttp.ClientSession() as session:
        for user_id in user_ids:
            try:
                async with session.post(url, json={
                    'chat_id': user_id,
                    'text': text,
                    'parse_mode': 'HTML'
                }) as resp:
                    if resp.status == 200:
                        sent += 1
                    else:
                        failed += 1
            except Exception:
                failed += 1

    return sent, failed