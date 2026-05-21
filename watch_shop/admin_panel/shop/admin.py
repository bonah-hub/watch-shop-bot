from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Watch, Order, OrderItem, MessageHistory, BotUser


@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'category', 'in_stock']
    list_filter = ['category', 'brand']
    search_fields = ['name', 'brand']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'username', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user_id', 'username']
    readonly_fields = ['created_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'price', 'quantity']
    search_fields = ['name']


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'user_message', 'bot_response', 'created_at']
    list_filter = ['created_at', 'username']
    search_fields = ['user_id', 'username', 'user_message']
    readonly_fields = ['created_at']


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'first_name', 'created_at', 'last_seen']
    search_fields = ['user_id', 'username', 'first_name']
    readonly_fields = ['created_at', 'last_seen']


# ── Кастомные ссылки в шапке Admin
class WatchShopAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('statistics/', self.admin_view(lambda r: redirect('/shop/statistics/'))),
            path('broadcast/', self.admin_view(lambda r: redirect('/shop/broadcast/'))),
        ]
        return custom + urls

    def each_context(self, request):
        ctx = super().each_context(request)
        ctx['custom_links'] = [
            {'url': '/shop/statistics/', 'label': '📊 Статистика'},
            {'url': '/shop/broadcast/', 'label': '📢 Рассылка'},
        ]
        return ctx