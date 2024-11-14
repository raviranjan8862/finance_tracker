# finances/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('update-transaction/<int:transaction_id>/', views.update_transaction, name='update_transaction'),
    path('delete-transaction/<int:id>/', views.delete_transaction, name='delete-transaction'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('set-saving-goal/', views.set_saving_goal, name='set_saving_goal'),
    path('edit-saving-goal/', views.edit_saving_goal, name='edit_saving_goal'),
    path('reports/', views.report_view, name='reports'),
    path('monthly-income-pie-chart/<int:month>/<int:year>/', views.monthly_income_pie_chart, name='monthly_income_pie_chart'),
]