import json
import os
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from store.catalog import CATEGORIES_TR, PRODUCTS, SPEC_KEYS_TR, specification_value_tr
from store.models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    User,
)


class Command(BaseCommand):
    help = (
        "Add the sample catalog and development admin without overwriting existing data"
    )

    @transaction.atomic
    def handle(self, *args, **options):
        if os.getenv("APP_ENV") != "development":
            raise CommandError(
                "Sample seeding is allowed only with APP_ENV=development"
            )
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@bytedesk.example")
        password = os.getenv("ADMIN_PASSWORD", "")
        if not User.objects.filter(username=username).exists():
            if len(password) < 12 or password.startswith("replace-with"):
                raise CommandError(
                    "Set ADMIN_PASSWORD to a development password of at least 12 characters"
                )
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
        images = json.loads(
            (Path(__file__).resolve().parents[2] / "catalog_images.json").read_text()
        )
        created = 0
        for index, (name, brand_name, category_name, price, stock, specs) in enumerate(
            PRODUCTS, 1
        ):
            category, _ = Category.objects.get_or_create(
                slug=slugify(category_name), defaults={"name": category_name}
            )
            if not category.name_tr:
                category.name_tr = CATEGORIES_TR.get(category_name, "")
                category.save(update_fields=["name_tr"])
            brand, _ = Brand.objects.get_or_create(
                slug=slugify(brand_name), defaults={"name": brand_name}
            )
            product, is_new = Product.objects.get_or_create(
                sku=f"BD-{index:04d}",
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "description": f"{name} for everyday work and a comfortable workspace. Sample catalog specifications and pricing.",
                    "price": Decimal(price),
                    "stock_quantity": stock,
                    "category": category,
                    "brand": brand,
                },
            )
            if is_new:
                created += 1
                for key, value in specs.items():
                    ProductSpecification.objects.create(
                        product=product, key=key, value=value
                    )
            if not product.description_tr:
                product.description_tr = f"{name}, günlük işler ve konforlu bir çalışma alanı için tasarlanmıştır. Ürün özellikleri ve fiyatlar örnek amaçlıdır."
                product.save(update_fields=["description_tr"])
            for specification in product.specifications.all():
                changed = []
                if not specification.key_tr:
                    specification.key_tr = SPEC_KEYS_TR.get(
                        specification.key, specification.key
                    )
                    changed.append("key_tr")
                if not specification.value_tr:
                    specification.value_tr = specification_value_tr(specification.value)
                    changed.append("value_tr")
                if changed:
                    specification.save(update_fields=changed)
            if not product.images.exists() and product.sku in images:
                ProductImage.objects.create(product=product, **images[product.sku])
            for image in product.images.filter(alt_text_tr=""):
                image.alt_text_tr = f"{product.name} ürün fotoğrafı"[:200]
                image.save(update_fields=["alt_text_tr"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created} products added; {Product.objects.count()} total."
            )
        )
