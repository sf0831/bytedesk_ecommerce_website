from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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

admin.site.register(User, UserAdmin)


@admin.register(Brand)
class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(TaxonomyAdmin):
    list_display = ("name", "name_tr", "slug")
    search_fields = ("name", "name_tr")


class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class SpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "brand",
        "price",
        "stock_quantity",
        "is_active",
    )
    list_editable = ("stock_quantity", "is_active")
    list_filter = ("category", "brand", "is_active")
    search_fields = ("name", "sku", "description", "description_tr", "brand__name", "category__name", "category__name_tr")
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("category", "brand")
    inlines = (ImageInline, SpecificationInline)
    readonly_fields = ("created_at", "updated_at")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "unit_price", "quantity", "subtotal")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "subtotal",
        "shipping",
        "total",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "shipping_name", "=id")
    list_select_related = ("user",)
    inlines = (OrderItemInline,)
    readonly_fields = tuple(f.name for f in Order._meta.fields if f.name != "status")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
    search_fields = ("title", "body", "product__name", "user__email")
    list_editable = ("is_approved",)
    readonly_fields = ("created_at",)
    list_select_related = ("product", "user")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "updated_at")
    inlines = (CartItemInline,)


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    inlines = (WishlistItemInline,)
