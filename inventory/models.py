from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Profile Model ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
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
    average_cost = models.PositiveIntegerField(default=0) 
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
    total_price = models.PositiveIntegerField() # This is the subtotal for this item (qty * unit_price)
    discount = models.PositiveIntegerField(default=0) # Allocated portion of the order-level flat discount
    unit_cost_at_sale = models.PositiveIntegerField(default=0) 
    date_sold = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def profit(self):
        total_cost = self.unit_cost_at_sale * self.quantity
        # Revenue is total_price minus the allocated discount
        return (self.total_price - self.discount) - total_cost

class Purchase(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                locked_item = Item.objects.select_for_update().get(pk=self.item.pk)
                total_current_value = locked_item.quantity * locked_item.average_cost
                new_purchase_value = self.quantity * self.unit_price
                total_new_qty = locked_item.quantity + self.quantity

                if total_new_qty > 0:
                    new_average_cost = (total_current_value + new_purchase_value) // total_new_qty
                    locked_item.average_cost = new_average_cost
                
                locked_item.quantity += self.quantity
                locked_item.save()
                self.item = locked_item

            super().save(*args, **kwargs)