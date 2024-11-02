from django.contrib import admin

# Register your models here.

from .models import Category, Transaction, SavingGoal

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



class SavingGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'yearly_goal', 'monthly_goal', 'current_saving', 'created_at')
    search_fields = ('user__username',)  # Allows searching by the username
    list_filter = ('created_at',)  # Allows filtering by creation date
    readonly_fields = ('monthly_goal', 'current_saving')  # Make monthly_goal and current_saving read-only

admin.site.register(SavingGoal, SavingGoalAdmin)

