from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Profile Model ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to auto-create Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Fixed: Only save profile if it actually exists
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# --- Existing Inventory Models ---
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
    average_cost = models.PositiveIntegerField(default=0)
    selling_price = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.quantity * self.average_cost

class SaleRecord(models.Model):
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.PositiveIntegerField()
    date_sold = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Purchase(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on create
            # WAC Calculation
            current_qty = self.item.quantity
            current_avg = self.item.average_cost
            new_qty = self.quantity
            new_price = self.unit_price

            total_qty = current_qty + new_qty
            if total_qty > 0:
                # Integer arithmetic for PKR
                total_cost = (current_qty * current_avg) + (new_qty * new_price)
                new_avg = total_cost // total_qty # Integer division
                self.item.average_cost = new_avg
                self.item.quantity = total_qty
                self.item.save()
        
        super().save(*args, **kwargs)