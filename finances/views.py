# finances/views.py

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from datetime import datetime
from decimal import Decimal
from .models import Transaction, SavingGoal
from .forms import TransactionForm, SavingGoalForm

# finances/views.py

@login_required
def dashboard(request):
    # Get the current month and year, or use the selected ones
    current_month = int(request.GET.get('month', datetime.now().month))
    current_year = int(request.GET.get('year', datetime.now().year))

    # Filter transactions based on the selected month and year
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).order_by('-date')

    # Calculate monthly income and expenses
    monthly_income = transactions.filter(transaction_type='income').aggregate(models.Sum('amount'))['amount__sum'] or 0
    monthly_expenses = transactions.filter(transaction_type='expense').aggregate(models.Sum('amount'))['amount__sum'] or 0
    monthly_balance = monthly_income - monthly_expenses

    # Calculate yearly income and expenses
    yearly_transactions = Transaction.objects.filter(
        user=request.user,
        date__year=current_year
    )
    yearly_income = yearly_transactions.filter(transaction_type='income').aggregate(models.Sum('amount'))['amount__sum'] or 0
    yearly_expenses = yearly_transactions.filter(transaction_type='expense').aggregate(models.Sum('amount'))['amount__sum'] or 0
    yearly_balance = yearly_income - yearly_expenses

    # Retrieve or create a saving goal for the user
    saving_goal, created = SavingGoal.objects.get_or_create(user=request.user, defaults={
        'yearly_goal': Decimal('0.00'),
        'monthly_goal': Decimal('0.00'),
        'current_saving': Decimal('0.00')
    })

    # Calculate remaining balance to be added to savings
    if monthly_balance > 0:
        saving_goal.current_saving += monthly_balance
        saving_goal.save()  # Update the saving goal with the new savings

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    context = {
        'transactions': transactions,
        'monthly_income': monthly_income,
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
from .models import Category

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



