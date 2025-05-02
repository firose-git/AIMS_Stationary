from djongo import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.text import slugify
import uuid
from decimal import Decimal

# 1) Category Model
class Category(models.Model):
    Category_id = models.CharField(max_length=24, primary_key=True)
    Category_description = models.CharField(max_length=255)
    Created_date = models.DateTimeField(auto_now_add=True)
    Update_date = models.DateTimeField(auto_now=True)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.Update_date = now()  # Force Update_date refresh
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Category_id} - {self.Category_description}"

    class Meta:
        verbose_name_plural = "Category"


# 2) Sub_Category Model
class Sub_Category(models.Model):
    SubCat_id = models.CharField(max_length=24, primary_key=True)
    SubCat_description = models.CharField(max_length=255)
    Category_id = models.ForeignKey('Category', on_delete=models.CASCADE)
    Created_date = models.DateTimeField(auto_now_add=True)
    Update_date = models.DateTimeField(auto_now=True)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.SubCat_description)
        self.Update_date = now()  # Force Update_date refresh
        super().save(*args, **kwargs)

    def __str__(self):
        return self.SubCat_description

    class Meta:
        verbose_name_plural = "Sub_Category"


# 3) Products Model
class Products(models.Model):
    prod_id = models.CharField(max_length=24, primary_key=True)
    Prod_description = models.CharField(max_length=255)
    Prod_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    Prod_price = models.DecimalField(max_digits=10, decimal_places=2)
    SubCategory = models.ForeignKey(Sub_Category, on_delete=models.CASCADE, related_name="products")
    Created_date = models.DateTimeField(auto_now_add=True)
    Update_date = models.DateTimeField(auto_now=True)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.Update_date = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Prod_description

    class Meta:
        verbose_name_plural = "Products"


# 4) Cart_table Model
class Cart_table(models.Model):
    Cart_id = models.CharField(max_length=24, unique=True, primary_key=True, default=lambda: f"CART{uuid.uuid4().hex[:6]}")
    prod_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=False)
    Created_date = models.DateTimeField(auto_now_add=True)
    Update_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.prod_id and self.quantity:
            self.total_price = self.quantity * Decimal(str(self.prod_id.Prod_price))
        else:
            self.total_price = Decimal("0.00")
        self.Update_date = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart ID: {self.Cart_id}, Product: {self.prod_id}, Quantity: {self.quantity}, Total Price: {self.total_price}, User: {self.User_id}"

    class Meta:
        verbose_name_plural = "Cart_table"


# 5) Stock_master Model
class Stock_master(models.Model):
    prod_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    Total = models.IntegerField()
    Min_Value = models.IntegerField(default=10)
    Created_date = models.DateTimeField(auto_now_add=True)
    Update_date = models.DateTimeField(auto_now=True)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.Update_date = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stock for Product {self.prod_id.Prod_description if self.prod_id else 'Unknown Product'}"

    @property
    def is_low_stock(self):
        return self.Total <= self.Min_Value

    class Meta:
        verbose_name_plural = "Stock_master"


# 6) Order_Details Model
class Order_Details(models.Model):
    Order_id = models.ForeignKey('Order_Table', on_delete=models.CASCADE)
    Prod_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    Created_date = models.DateTimeField(auto_now_add=True)
    Update_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.Update_date = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.Order_id.Order_id} - Product {self.Prod_id.Prod_description}"

    class Meta:
        verbose_name_plural = "Order_Details"


# 7) Order_Table Model
class Order_Table(models.Model):
    APPROVED = 'Approved'
    PENDING = 'Pending'
    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
    ]

    Order_id = models.AutoField(primary_key=True)
    Order_date = models.DateTimeField(auto_now_add=True)
    User_id = models.ForeignKey(User, on_delete=models.CASCADE)
    Status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"Order {self.Order_id} - {self.Status}"

    class Meta:
        verbose_name_plural = "Order_Table"


# 8) Contact Model
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


# 9) Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
