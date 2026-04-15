from django.contrib import admin

# Register your models here.
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'created_at')
    search_fields = ('word', 'translation')
