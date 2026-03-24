from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    # image = models.ImageField(upload_to='categories/', blank=True, null=True) 
    

    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name 
    


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    stock = models.PositiveBigIntegerField(default=1)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # image = models.ImageField(upload_to='products/%Y/%m/%d') # products/25/10/2025
    image = CloudinaryField('image', blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['available']),
        ]

    def __str__(self):
        return self.name 
    
    # Get average rating for the product
    def average_ratings(self):
        """Calculate and return average rating for the product."""
        ratings = self.ratings.all()
        if ratings.count() > 0:
            # Fixed: Method name typo (average_ratins -> average_ratings)
            return round(sum([i.rating for i in ratings]) / ratings.count(), 2)
        return 0  # Return 0 if no ratings exist




class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # Prevent multiple ratings from same user per product
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"
    


    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
        ]
        
    # total price
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all()) # 100
    # total koita item
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all()) 
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveBigIntegerField(default=1)

    class Meta:
       unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} X {self.product.name}" # 4 X Shirt
    def get_cost(self):
        return self.quantity*self.product.price         # 20
    


    
class Order(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    PAYMENT_METHODS = (
        ('cod', 'Cash On Delivery'),
        ('sslcommerz', 'SSLCommerz'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    username = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=12)
    note = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)


    def __str__(self):
        return f"Order #{self.id}" # Order #2
    
    # order item er sum lagbe
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.order_items.all()) # 100
    

    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_cost(self):
        return self.quantity*self.product.price  # 20
        
