# Learning Log: Stationery Inventory SaaS

## 1. Understanding SQL Relationships (ForeignKey)
In our database schema, we use `ForeignKey` to establish relationships between tables. This ensures data integrity and logical organization.

*   **User -> Category/Item/Purchase**: We added `user = models.ForeignKey(User, ...)` to every model. This creates a "One-to-Many" relationship where one User can have many Items, but each Item belongs to exactly one User. This is crucial for a SaaS application to ensure **Data Isolation**—User A should never see User B's inventory.
*   **Category -> Item**: An Item belongs to a Category. If we delete a Category, we might want to delete all its Items (CASCADE) or keep them. We chose `on_delete=models.CASCADE` for simplicity, meaning if "Pens" category is deleted, all pens are deleted.
*   **Item -> Purchase**: A Purchase is a record of buying a specific Item. This links the transaction history to the inventory object.

## 2. The "Brain": Overriding the `save()` Method
We implemented business logic directly in the `Purchase` model's `save()` method. This is a powerful Django pattern to automate side effects.

### Why?
Instead of manually updating the Item's quantity and cost every time we create a Purchase in a View, we encapsulate this logic in the Model. This ensures that *no matter how* a Purchase is created (Admin panel, API, or View), the Inventory is always updated correctly.

### The Logic (Weighted Average Cost)
When a new Purchase is saved:
1.  We fetch the current `quantity` and `average_cost` of the related Item.
2.  We calculate the new Weighted Average Cost (WAC) using the formula:
    `New Avg = ((Current Qty * Current Avg) + (New Qty * New Price)) / (Total Qty)`
3.  We update the Item's `quantity` and `average_cost`.
4.  We save the Item.
5.  Finally, we save the Purchase record itself.

This guarantees that our inventory valuation is always accurate based on what we actually paid.
