from django.db import models
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
        if not self.pk:  # Only on create
            current_qty = self.item.quantity
            
            # Logic: If out of stock, reset cost. If in stock, cost remains unless manually updated via Edit.
            if current_qty <= 0:
                self.item.average_cost = self.unit_price
            
            self.item.quantity += self.quantity
            self.item.save()
        
        super().save(*args, **kwargs)