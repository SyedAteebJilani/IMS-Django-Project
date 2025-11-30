import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_saas.settings')
django.setup()

from inventory.models import Item, Category, SaleRecord
from django.contrib.auth.models import User

def clean_and_seed():
    user = User.objects.get(username='admin')
    
    # Cleanup
    print("Cleaning up...")
    SaleRecord.objects.filter(user=user).delete()
    Item.objects.filter(user=user, name='Test Pen').delete()
    Category.objects.filter(user=user, name='General').delete()
    
    # Seed
    print("Seeding data...")
    category = Category.objects.create(name='General', user=user)
    item = Item.objects.create(
        name='Test Pen',
        category=category,
        company='Dollar',
        selling_price=500,
        average_cost=400,
        quantity=100,
        user=user
    )
    print(f"Created Item: {item.name} with Qty: {item.quantity}")

if __name__ == '__main__':
    clean_and_seed()
