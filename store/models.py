from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=30,
        default="Order Placed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=200)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product_name


class Product(models.Model):

    CATEGORY_CHOICES = [
        ('Dresses', 'Dresses'),
        ('Toys', 'Toys'),
        ('Mobiles', 'Mobiles'),
        ('Footwear', 'Footwear'),
        ('Accessories', 'Accessories'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home & Living'),
        ('Beauty', 'Beauty'),
    ]

    name = models.CharField(max_length=120)

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    stock = models.PositiveIntegerField(default=0)

    image_url = models.URLField(blank=True ,  null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name