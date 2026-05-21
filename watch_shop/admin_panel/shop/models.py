# Добавь это в admin_panel/shop/models.py
# (к уже существующей модели Watch)

from django.db import models


class Watch(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    brand = models.CharField(max_length=100)
    description = models.TextField()
    in_stock = models.IntegerField(default=0)
    category = models.CharField(max_length=50, default='classic')  # classic / smart
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Часы"
        verbose_name_plural = "Часы"


class Order(models.Model):
    user_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True)
    total = models.IntegerField()
    status = models.CharField(max_length=50, default='Принят')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.user_id}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    watch_id = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"


class MessageHistory(models.Model):
    """История диалогов пользователей с ботом"""
    user_id = models.CharField(max_length=50, verbose_name="ID пользователя")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    user_message = models.TextField(verbose_name="Сообщение пользователя")
    bot_response = models.TextField(verbose_name="Ответ бота")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self):
        return f"[{self.created_at.strftime('%d.%m.%Y %H:%M')}] {self.username or self.user_id}: {self.user_message[:50]}"

    class Meta:
        verbose_name = "История сообщений"
        verbose_name_plural = "История сообщений"
        ordering = ['-created_at']

class BotUser(models.Model):
    """Все пользователи которые написали боту"""
    user_id = models.CharField(max_length=50, unique=True, verbose_name="ID пользователя")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Первый визит")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Последний визит")

    def __str__(self):
        return f"@{self.username or self.user_id} ({self.first_name})"

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"
        ordering = ['-created_at']