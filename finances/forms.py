# finances/forms.py

from django import forms
from .models import Transaction,SavingGoal

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'amount', 'description']



class SavingGoalForm(forms.Form):
    yearly_goal = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Yearly Saving Goal",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your yearly saving goal'})
    )

