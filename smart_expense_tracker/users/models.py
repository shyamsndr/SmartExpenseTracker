from django.db import models
from django.db.models import UniqueConstraint

class User(models.Model):
    u_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.email
    
class SourceOfIncome(models.Model):
    source_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'name'], name='unique_user_source')
        ]

    def __str__(self):
        return self.name
    
class PaymentMethod(models.Model):
    method_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    name = models.CharField(max_length=255)  # Payment method name (Cash, UPI, etc.)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'name'], name='unique_user_payment_method')
        ]

    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Link to User
    name = models.CharField(max_length=100)  # Category Name (e.g., Food, Rent, Shopping)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'name'], name='unique_user_category')
        ]

    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Link to Category
    limit = models.DecimalField(max_digits=10, decimal_places=2)  # Budget Limit Amount

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'category'], name='unique_user_category_budget')
        ]

    def __str__(self):
        return f"{self.user.email} - {self.category.name} - ₹{self.limit}"
    
class Income(models.Model):
    income_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    source = models.ForeignKey(SourceOfIncome, on_delete=models.CASCADE)  # Link to Source
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Store amount properly
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)  # Cash, UPI, etc.
    description = models.TextField(blank=True, null=True)  # Optional Description
    date = models.DateField()  # Store Date
    time = models.TimeField()  # Store Time
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically add timestamp

    def __str__(self):
        return f"{self.user.email} - {self.amount}"
    
class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Link to Category
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)  # Link to Payment Method
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Store amount properly
    description = models.TextField(blank=True, null=True)  # Optional Description
    date = models.DateField()  # Store Date
    time = models.TimeField()  # Store Time
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically add timestamp

    def __str__(self):
        return f"{self.user.email} - {self.amount} ({self.category.name})"