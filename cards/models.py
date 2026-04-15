from django.db import models

# Create your models here.

class Card(models.Model):
    # Поля моделиpython manage.py createsuperuser
    word = models.CharField(max_length=100, verbose_name="Слово")
    translation = models.CharField(max_length=100, verbose_name="Перевод")
    example = models.TextField(blank=True, verbose_name="Пример использования")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")


    def __str__(self):
        return f"{self.word} — {self.translation}"

    # Настройки отображения в админке
    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
