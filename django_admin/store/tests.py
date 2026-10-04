import os
from decimal import Decimal
from unittest.mock import patch

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import (
    Brand,
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductSpecification,
    Review,
    User,
    Wishlist,
    WishlistItem,
)


class StoreTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="safe-test-password",
        )
        cls.category = Category.objects.create(name="Keyboards", slug="keyboards")
        cls.brand = Brand.objects.create(name="Keychron", slug="keychron")
        cls.product = Product.objects.create(
            name="Test Keyboard",
            slug="test-keyboard",
            sku="TEST-1",
            price=Decimal("49.00"),
            stock_quantity=3,
            category=cls.category,
            brand=cls.brand,
        )

    def rejects(self, create):
        with self.assertRaises(IntegrityError), transaction.atomic():
            create()

    def test_password_hashed(self):
        self.assertNotEqual(self.user.password, "safe-test-password")
        self.assertTrue(self.user.check_password("safe-test-password"))

    def test_product_unique_and_amount_constraints(self):
        for overrides in (
            {"sku": "TEST-1", "slug": "other"},
            {"sku": "OTHER", "slug": "test-keyboard"},
            {"sku": "NEG", "slug": "negative", "price": -1},
            {"sku": "STOCK", "slug": "stock", "stock_quantity": -1},
        ):
            values = {
                "name": "Other",
                "price": 10,
                "category": self.category,
                "brand": self.brand,
            }
            values.update(overrides)
            self.rejects(lambda: Product.objects.create(**values))

    def test_taxonomy_protected_and_unique(self):
        self.rejects(lambda: Category.objects.create(name="Duplicate", slug="keyboards"))
        self.rejects(lambda: Brand.objects.create(name="Duplicate", slug="keychron"))
        with self.assertRaises(ProtectedError):
            self.category.delete()
        with self.assertRaises(ProtectedError):
            self.brand.delete()

    def test_email_case_insensitive_unique(self):
        self.rejects(
            lambda: User.objects.create_user(username="second", email="CUSTOMER@example.com")
        )

    def test_cart_and_wishlist_constraints(self):
        cart = Cart.objects.create(user=self.user)
        wishlist = Wishlist.objects.create(user=self.user)
        self.rejects(lambda: Cart.objects.create(user=self.user))
        self.rejects(lambda: Wishlist.objects.create(user=self.user))
        CartItem.objects.create(cart=cart, product=self.product)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product)
        self.rejects(lambda: CartItem.objects.create(cart=cart, product=self.product))
        self.rejects(lambda: WishlistItem.objects.create(wishlist=wishlist, product=self.product))
        CartItem.objects.filter(cart=cart).delete()
        self.rejects(lambda: CartItem.objects.create(cart=cart, product=self.product, quantity=0))

    def test_review_constraints(self):
        self.rejects(
            lambda: Review.objects.create(
                user=self.user, product=self.product, rating=6, title="Bad"
            )
        )
        review = Review.objects.create(user=self.user, product=self.product, rating=5, title="Good")
        self.assertFalse(review.is_approved)
        self.rejects(
            lambda: Review.objects.create(
                user=self.user, product=self.product, rating=4, title="Again"
            )
        )

    def test_specification_unique(self):
        ProductSpecification.objects.create(product=self.product, key="Layout", value="75%")
        self.rejects(
            lambda: ProductSpecification.objects.create(
                product=self.product, key="Layout", value="65%"
            )
        )

    def test_order_snapshot_survives_product_deletion(self):
        order = Order.objects.create(
            user=self.user,
            subtotal=49,
            shipping=5,
            total=54,
            shipping_name="Customer",
            shipping_address="1 Main St",
            shipping_city="City",
            shipping_postal_code="12345",
            shipping_country="US",
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            unit_price=49,
            quantity=1,
            subtotal=49,
        )
        self.product.name = "Renamed"
        self.product.price = 99
        self.product.save()
        self.product.delete()
        item.refresh_from_db()
        self.assertIsNone(item.product_id)
        self.assertEqual(item.product_name, "Test Keyboard")
        self.assertEqual(item.unit_price, Decimal("49.00"))
        with self.assertRaises(ProtectedError):
            self.user.delete()

    def test_seed_idempotent_and_preserves_changes(self):
        with patch.dict(
            os.environ,
            {"APP_ENV": "development", "ADMIN_PASSWORD": "safe-development-password"},
        ):
            call_command("seed_store")
            product = Product.objects.get(sku="BD-0001")
            self.assertTrue(product.description_tr)
            self.assertEqual(product.category.name_tr, "Klavyeler")
            spec = product.specifications.first()
            self.assertTrue(spec.key_tr)
            spec.key_tr = "Özel başlık"
            spec.value_tr = "Özel değer"
            spec.save()
            product.description_tr = "Yönetici tarafından düzenlenen açıklama"
            category = product.category
            category.name_tr = "Özel kategori"
            category.save()
            product.price = 1
            product.stock_quantity = 2
            product.save()
            specs = ProductSpecification.objects.count()
            self.assertEqual(ProductImage.objects.count(), 20)
            image = product.images.get()
            self.assertTrue(image.alt_text_tr)
            image.alt_text_tr = "Özel ürün görseli"
            image.url = "/images/custom-admin-photo.jpg"
            image.save()
            call_command("seed_store")
        product.refresh_from_db()
        self.assertEqual(product.description_tr, "Yönetici tarafından düzenlenen açıklama")
        self.assertEqual(product.category.name_tr, "Özel kategori")
        spec.refresh_from_db()
        self.assertEqual((spec.key_tr, spec.value_tr), ("Özel başlık", "Özel değer"))
        self.assertEqual(product.price, 1)
        self.assertEqual(product.stock_quantity, 2)
        self.assertEqual(Product.objects.count(), 21)
        self.assertEqual(ProductSpecification.objects.count(), specs)
        self.assertEqual(ProductImage.objects.count(), 20)
        self.assertEqual(product.images.get().url, "/images/custom-admin-photo.jpg")
        self.assertEqual(product.images.get().alt_text_tr, "Özel ürün görseli")
        self.assertTrue(
            User.objects.get(username="admin").check_password("safe-development-password")
        )

    def test_admin_pages_and_inline_products(self):
        admin = User.objects.create_superuser(
            username="staff", email="staff@example.com", password="safe-test-password"
        )
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        self.client.force_login(admin)
        for url in (
            "/admin/",
            "/admin/store/product/",
            f"/admin/store/product/{self.product.pk}/change/",
            "/admin/store/order/",
            "/admin/store/review/",
        ):
            self.assertEqual(self.client.get(url).status_code, 200)
        detail = self.client.get(f"/admin/store/product/{self.product.pk}/change/")
        self.assertContains(detail, "Description (Turkish)")
        self.assertContains(detail, "Alt text (Turkish)")
        self.assertContains(detail, "Key (Turkish)")
        self.assertContains(detail, "Value (Turkish)")
        response = self.client.get("/admin/store/product/")
        self.assertContains(response, "Test Keyboard")
