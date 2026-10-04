from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    auth_version = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "users"
        constraints = [
            models.UniqueConstraint(models.functions.Lower("email"), name="unique_user_email_ci")
        ]


class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=120)
    name_tr = models.CharField(
        max_length=120, blank=True, default="", verbose_name="Name (Turkish)"
    )
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = "brands"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(Timestamped):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    sku = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    description_tr = models.TextField(
        blank=True, default="", verbose_name="Description (Turkish)"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="product_price_nonnegative"
            )
        ]
        indexes = [models.Index(fields=["is_active", "price"], name="product_active_price_idx")]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.CharField(max_length=500, help_text="Local asset path or image URL")
    alt_text = models.CharField(max_length=200)
    alt_text_tr = models.CharField(
        max_length=200, blank=True, default="", verbose_name="Alt text (Turkish)"
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "product_images"
        ordering = ["position", "id"]


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=250)
    key_tr = models.CharField(
        max_length=100, blank=True, default="", verbose_name="Key (Turkish)"
    )
    value_tr = models.CharField(
        max_length=250, blank=True, default="", verbose_name="Value (Turkish)"
    )

    class Meta:
        db_table = "product_specifications"
        constraints = [
            models.UniqueConstraint(fields=["product", "key"], name="unique_product_spec_key")
        ]


class Cart(Timestamped):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    class Meta:
        db_table = "carts"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_cart_product"),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1), name="cart_quantity_positive"
            ),
        ]


class Wishlist(Timestamped):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")

    class Meta:
        db_table = "wishlists"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = "wishlist_items"
        constraints = [
            models.UniqueConstraint(fields=["wishlist", "product"], name="unique_wishlist_product")
        ]


class Order(Timestamped):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    checkout_key = models.UUIDField(null=True, blank=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_name = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=300)
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"], name="order_user_date_idx")]
        constraints = [
            models.UniqueConstraint(fields=["user", "checkout_key"], name="unique_order_checkout_key"),
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0, shipping__gte=0, total__gte=0),
                name="order_amounts_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(total=models.F("subtotal") + models.F("shipping")),
                name="order_total_matches",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "pending",
                        "confirmed",
                        "processing",
                        "shipped",
                        "delivered",
                        "cancelled",
                    ]
                ),
                name="order_valid_status",
            ),
        ]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1, unit_price__gte=0, subtotal__gte=0),
                name="order_item_valid_amounts",
            ),
            models.CheckConstraint(
                condition=models.Q(subtotal=models.F("unit_price") * models.F("quantity")),
                name="order_item_subtotal_matches",
            ),
        ]


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=160)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_review"),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_range",
            ),
        ]
