from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Profile Model ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # NEW: Business Name for Sidebar Branding
    business_name = models.CharField(max_length=100, default="IMS", blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# --- Inventory Models ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Item(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.CharField(max_length=100, default="Unknown")
    quantity = models.IntegerField(default=0)
    average_cost = models.PositiveIntegerField(default=0) # Acts as "Current Buying Price"
    selling_price = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.quantity * self.average_cost

class SaleRecord(models.Model):
    order_id = models.CharField(max_length=20, blank=True, null=True)
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.PositiveIntegerField()
    unit_cost_at_sale = models.PositiveIntegerField(default=0) 
    date_sold = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def profit(self):
        total_cost = self.unit_cost_at_sale * self.quantity
        return self.total_price - total_cost

class Purchase(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Start a database transaction to ensure atomicity
        with transaction.atomic():
            # Only run this logic if the Purchase is new (pk is None)
            if not self.pk:
                # 1. Lock the Item row to prevent race conditions
                locked_item = Item.objects.select_for_update().get(pk=self.item.pk)

                # 2. Logic: Weighted Average Cost Calculation
                # Calculate the total value of existing inventory
                total_current_value = locked_item.quantity * locked_item.average_cost
                
                # Calculate the value of the new purchase
                new_purchase_value = self.quantity * self.unit_price
                
                # Determine new total quantity
                total_new_qty = locked_item.quantity + self.quantity

                # Calculate new average cost (Total Value / Total Quantity)
                # We guard against division by zero if total_new_qty is 0 or less
                if total_new_qty > 0:
                    new_average_cost = (total_current_value + new_purchase_value) // total_new_qty
                    locked_item.average_cost = new_average_cost
                
                # 3. Logic: Update Quantity
                locked_item.quantity += self.quantity
                locked_item.save()

                # 4. Update the local instance to match the locked data
                self.item = locked_item

            # 5. Save the Purchase record normally
            super().save(*args, **kwargs)