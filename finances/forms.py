# finances/forms.py

from django import forms
from .models import Transaction,SavingGoal

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'amount', 'description']



# forms.py
from django import forms
from .models import SavingGoal

from django import forms
from .models import SavingGoal

class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ['yearly_goal']  # Only allowing the user to update the yearly goal

    def clean_yearly_goal(self):
        yearly_goal = self.cleaned_data['yearly_goal']
        if yearly_goal <= 0:
            raise forms.ValidationError('Yearly goal must be greater than zero.')
        return yearly_goal

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Automatically update the monthly goal based on the yearly goal
        instance.monthly_goal = instance.yearly_goal / 12
        if commit:
            instance.save()
        return instance



