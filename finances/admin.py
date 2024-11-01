from django.contrib import admin

# Register your models here.

from .models import Category, Transaction, SavingsGoal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'category', 'amount', 'date', 'user')
    search_fields = ('transaction_type', 'category__name', 'user__username')
    list_filter = ('transaction_type', 'category', 'date', 'user')
    ordering = ('-date',)  # Orders by date in descending order

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_amount', 'target_amount', 'deadline', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('deadline', 'user')
    ordering = ('deadline',)  # Orders by deadline in ascending order

