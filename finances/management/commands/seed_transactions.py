# finances/management/commands/seed_transactions.py

import random
from django.core.management.base import BaseCommand
from faker import Faker
from finances.models import Transaction, Category
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed the Transaction model with fake data'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='The number of transactions to create')

    def handle(self, *args, **options):
        fake = Faker()
        num_records = options['number']
        users = User.objects.all()

        # Define income and expense category names
        income_category_names = ["salary", "Agriculture_income", "Bonus"]
        expense_category_names = ["Rent", "Groceries", "Entertainment", "Utilities","Transport","Food"]

        # Filter categories based only on specified names
        income_categories = Category.objects.filter(name__in=income_category_names)
        expense_categories = Category.objects.filter(name__in=expense_category_names)

        if not users.exists() or (not income_categories.exists() and not expense_categories.exists()):
            self.stdout.write(self.style.ERROR('Please create at least one user and ensure that specified income/expense categories exist.'))
            return

        for _ in range(num_records):
            user = random.choice(users)
            transaction_type = random.choice(['income', 'expense'])

            # Select a category from the specified list based on transaction_type
            category = random.choice(income_categories if transaction_type == 'income' else expense_categories)
            amount = round(random.uniform(10, 1000), 2)
            description = fake.sentence()

            # Generate a random date within the past year
            days_in_past = random.randint(0, 365)
            date = timezone.now().date() - timedelta(days=days_in_past)

            # Create the transaction
            Transaction.objects.create(
                user=user,
                transaction_type=transaction_type,
                category=category,
                amount=amount,
                description=description,
                date=date,
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_records} fake transactions'))
