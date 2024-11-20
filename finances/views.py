# finances/views.py

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Q
from datetime import datetime
from decimal import Decimal
from .models import Transaction, SavingGoal, Category
from .forms import TransactionForm, SavingGoalForm
import json
# finances/views.py


@login_required
def dashboard(request):
    current_month = int(request.GET.get('month', datetime.now().month))
    current_year = int(request.GET.get('year', datetime.now().year))

    # Filter transactions based on the selected month and year
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).order_by('-date')

    # Calculate monthly income and expenses
    monthly_incomes = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_balance = monthly_incomes - monthly_expenses

    # Calculate yearly income and expenses
    yearly_transactions = Transaction.objects.filter(
        user=request.user,
        date__year=current_year
    )
    yearly_income = yearly_transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_expenses = yearly_transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_balance = yearly_income - yearly_expenses

    # Retrieve or create a saving goal for the user
    saving_goal, created = SavingGoal.objects.get_or_create(user=request.user, defaults={
        'yearly_goal': Decimal('0.00'),
        'monthly_goal': Decimal('0.00'),
        'current_saving': Decimal('0.00')
    })
    category_labels, category_values = get_expense_by_category(request, current_month, current_year)
    monthly_income_data, monthly_expense_data = get_monthly_income_expense_data(request.user, current_year)
    daily_income_data, daily_expense_data = get_daily_income_expense_data(request.user, current_year, current_month)

    # Calculate remaining balance to be added to savings
    if monthly_balance > 0:
        saving_goal.current_saving += monthly_balance
        saving_goal.save()

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    context = {
        'transactions': transactions,
        'monthly_income': monthly_incomes,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_balance,
        'yearly_income': yearly_income,
        'yearly_expenses': yearly_expenses,
        'yearly_balance': yearly_balance,
        'saving_goal': saving_goal,
        'month_names': month_names, 
        'current_month': current_month,
        'current_month_name': month_names[current_month - 1],
        'current_year': current_year,
        'monthly_income_data': monthly_income_data,
        'monthly_expense_data': monthly_expense_data,
        'daily_income_data': daily_income_data,
        'daily_expense_data': daily_expense_data,
        'category_labels': category_labels,
        'category_values': category_values,
    }
    return render(request, 'finances/dashboard.html', context)





@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')  # Redirect back to the dashboard after saving
    else:
        form = TransactionForm()
    
    return render(request, 'finances/add_transaction.html', {'form': form})

# finances/views.py

from django.http import JsonResponse


def filter_categories(request):
    transaction_type = request.GET.get('transaction_type')
    categories = Category.objects.filter(transaction_type=transaction_type)
    category_data = [{"id": cat.id, "name": cat.name} for cat in categories]
    return JsonResponse(category_data, safe=False)


# finances/views.py
@login_required
def update_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)  # Ensures only the logged-in user's transactions are accessed

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to dashboard after updating
    else:
        form = TransactionForm(instance=transaction)  # Load form with existing transaction data

    return render(request, 'finances/update_transaction.html', {'form': form, 'transaction': transaction})

@login_required
def delete_transaction(request, id):
    # Get the transaction object by ID or return a 404 if it doesn't exist
    transaction = get_object_or_404(Transaction, id=id)
    
    # Perform the deletion
    transaction.delete()
    
    # Optionally, add a message to confirm deletion
    messages.success(request, 'Transaction deleted successfully.')
    
    # Redirect to the main dashboard or transactions list page
    return redirect('dashboard')  # Replace 'dashboard' with your desired redirect path

def transaction_history(request):
    transactions = Transaction.objects.filter(user_id=1)  # Adjust to filter based on the logged-in user
    current_month = int(request.GET.get('month', datetime.now().month))
    current_year = int(request.GET.get('year', datetime.now().year))
        # Filter transactions based on the selected month and year
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).order_by('-date')

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    context = {
        'transactions': transactions,
        'month_names': month_names, 
        'current_month': current_month,
        'current_month_name': month_names[current_month - 1],
        'current_year': current_year,
    }
    return render(request, 'finances/transaction_history.html', context)

def set_saving_goal(request):
    if request.method == 'POST':
        form = SavingGoalForm(request.POST)
        if form.is_valid():
            yearly_goal = form.cleaned_data['yearly_goal']
            monthly_goal = Decimal(yearly_goal) / 12
            SavingGoal.objects.create(
                yearly_goal=yearly_goal,
                monthly_goal=monthly_goal,
                user=request.user
            )
            return redirect('dashboard')  # Redirect to dashboard or another relevant page
    else:
        form = SavingGoalForm()
    return render(request, 'finances/set_saving_goal.html', {'form': form})

@login_required
def edit_saving_goal(request):
    # Get the user's saving goal or create a new one if it doesn't exist
    saving_goal = SavingGoal.objects.filter(user=request.user).first()
    
    # If no saving goal exists, create one (optional)
    if not saving_goal:
        saving_goal = SavingGoal(user=request.user, yearly_goal=0, monthly_goal=0)

    if request.method == 'POST':
        form = SavingGoalForm(request.POST, instance=saving_goal)
        if form.is_valid():
            form.save()  # Save the updated saving goal
            messages.success(request, 'Saving goal updated successfully.')
            return redirect('dashboard')  # Redirect to the dashboard after saving
    else:
        form = SavingGoalForm(instance=saving_goal)  # Load the form with the current saving goal

    return render(request, 'finances/edit_saving_goal.html', {'form': form})


import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from .models import Transaction, SavingGoal


@login_required
def report_view(request):
    current_month = int(request.GET.get('month', datetime.now().month))
    current_year = int(request.GET.get('year', datetime.now().year))

    # Filter transactions for the current month and year
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).order_by('-date')

    # Calculate monthly income and expenses
    monthly_incomes = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_balance = monthly_incomes - monthly_expenses

    # Retrieve or create a saving goal for the user
    saving_goal, _ = SavingGoal.objects.get_or_create(user=request.user, defaults={
        'yearly_goal': Decimal('0.00'),
        'monthly_goal': Decimal('0.00'),
        'current_saving': Decimal('0.00')
    })

    # Calculate monthly saving
    monthly_saving = monthly_balance if monthly_balance > 0 else 0

    # Data for the donut chart
    monthly_goal = saving_goal.monthly_goal
    remaining_goal = max(monthly_goal - monthly_saving, Decimal('0.00'))

    monthly_saving_donut_data = {
        'labels': ['Monthly Saving', 'Remaining Goal'],
        'values': [
            float(monthly_saving),
            float(remaining_goal)
        ]
    }

    # Include additional context data for other charts
    category_labels, category_values = get_expense_by_category(request, current_month, current_year)
    monthly_income_data, monthly_expense_data = get_monthly_income_expense_data(request.user, current_year)
    daily_income_data, daily_expense_data = get_daily_income_expense_data(request.user, current_year, current_month)

    # Month names for dropdown or display
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    context = {
        'transactions': transactions,
        'monthly_income': monthly_incomes,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_balance,
        'saving_goal': saving_goal,
        'monthly_saving_donut_data': json.dumps(monthly_saving_donut_data),  # Serialized for the template
        'month_names': month_names,
        'current_month': current_month,
        'current_month_name': month_names[current_month - 1],
        'current_year': current_year,
        'monthly_income_data': monthly_income_data,
        'monthly_expense_data': monthly_expense_data,
        'daily_income_data': daily_income_data,
        'daily_expense_data': daily_expense_data,
        'category_labels': category_labels,
        'category_values': category_values,
    }

    return render(request, 'finances/reports.html', context)







from django.db.models import Sum

def get_monthly_income_expense_data(user, year):
    monthly_income_data = []
    monthly_expense_data = []
    yearly_transactions = Transaction.objects.filter(user=user, date__year=year)
    
    for month in range(1, 13):
        monthly_income = yearly_transactions.filter(
            transaction_type='income', date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_expense = yearly_transactions.filter(
            transaction_type='expense', date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_income_data.append(monthly_income)
        monthly_expense_data.append(monthly_expense)
    
    return monthly_income_data, monthly_expense_data

from datetime import datetime
from django.db.models import Sum
from .models import Transaction

def get_daily_income_expense_data(user, year, month):
    daily_income_data = []
    daily_expense_data = []

    for day in range(1, 32):  # Assume maximum of 31 days in a month
        try:
            day_income = Transaction.objects.filter(
                user=user,
                date__year=year,
                date__month=month,
                date__day=day,
                transaction_type='income'
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            day_expense = Transaction.objects.filter(
                user=user,
                date__year=year,
                date__month=month,
                date__day=day,
                transaction_type='expense'
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            daily_income_data.append(day_income)
            daily_expense_data.append(day_expense)

        except ValueError:
            break  # Break if the day is invalid (e.g., February 30)

    return daily_income_data, daily_expense_data


def get_expense_by_category(request, month, year):
    expenses_by_category = (
        Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__year=year,
            date__month=month
        )
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
    )

    category_labels = [expense['category__name'] for expense in expenses_by_category]
    category_values = [expense['total_amount'] for expense in expenses_by_category]

    return category_labels, category_values



def monthly_income_pie_chart(request, month, year):
    income_data = (
        Transaction.objects.filter(
            user=request.user,
            transaction_type='income',
            date__month=month,
            date__year=year
        )
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('category__name')
    )
    
    category_labels = [entry['category__name'] for entry in income_data]
    category_values = [entry['total_amount'] for entry in income_data]
    
    return JsonResponse({
        'category_labels': category_labels,
        'category_values': category_values
    })

from django.shortcuts import render
from django.db.models import Sum
from .models import SavingGoal, Transaction

def saving_goal_chart(request):
    # Fetch the user's saving goal and current saving
    saving_goal = SavingGoal.objects.filter(user=request.user).first()
    yearly_goal = saving_goal.yearly_goal if saving_goal else 0
    current_saving = saving_goal.current_saving if saving_goal else 0

    remaining_goal = yearly_goal - current_saving if yearly_goal > current_saving else 0

    # Pass data to the template
    context = {
        'current_saving': current_saving,
        'remaining_goal': remaining_goal,
        'yearly_goal': yearly_goal,
    }
    return render(request, 'your_app/saving_goal_chart.html', context)





