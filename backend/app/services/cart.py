from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from ..models import Cart, CartItem, Product, User, Wishlist
from ..schemas.cart import CartLine, CartResponse
from .errors import StoreError

FREE_SHIPPING = Decimal("100.00")
SHIPPING_FEE = Decimal("8.00")


def totals(subtotal: Decimal, has_items: bool = True) -> tuple[Decimal, Decimal]:
    shipping = (
        SHIPPING_FEE if has_items and subtotal < FREE_SHIPPING else Decimal("0.00")
    )
    return (shipping, subtotal + shipping)


def lock_customer(db: Session, user_id: int) -> None:
    # Serialize cart, wishlist and checkout mutations for this customer.
    db.execute(select(User.id).where(User.id == user_id).with_for_update())


def container(db: Session, model: type[Cart] | type[Wishlist], user_id: int):
    result = db.scalar(select(model).where(model.user_id == user_id))
    if result is None:
        now = datetime.now(timezone.utc)
        result = model(user_id=user_id, created_at=now, updated_at=now)
        db.add(result)
        db.flush()
    return result


def product_options():
    return [
        selectinload(Product.category),
        selectinload(Product.brand),
        selectinload(Product.images),
    ]


def get_lines(db: Session, cart_id: int) -> list[CartItem]:
    return list(
        db.scalars(
            select(CartItem)
            .where(CartItem.cart_id == cart_id)
            .order_by(CartItem.id)
            .options(selectinload(CartItem.product).options(*product_options()))
        )
    )


def read_cart(db: Session, user_id: int) -> CartResponse:
    cart = db.scalar(select(Cart).where(Cart.user_id == user_id))
    lines = get_lines(db, cart.id) if cart else []
    items = [
        CartLine(
            id=line.id,
            product=line.product,
            quantity=line.quantity,
            subtotal=line.product.price * line.quantity,
            available=line.product.is_active
            and line.product.stock_quantity >= line.quantity,
        )
        for line in lines
    ]
    subtotal = sum((item.subtotal for item in items), Decimal("0.00"))
    (shipping, total) = totals(subtotal, bool(items))
    return CartResponse(
        items=items,
        item_count=sum(item.quantity for item in items),
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        free_shipping_threshold=FREE_SHIPPING,
    )


def valid_quantity(product: Product, quantity: int) -> None:
    if not product.is_active:
        raise StoreError(
            409,
            f"{product.name} is no longer available. Remove it from your cart.",
            params={"product": product.name},
            code="product_unavailable",
        )
    if quantity > product.stock_quantity:
        raise StoreError(
            409,
            f"Only {product.stock_quantity} of {product.name} are available.",
            params={"product": product.name, "stock": product.stock_quantity},
            code="insufficient_stock",
        )
    if quantity > 10000:
        raise StoreError(
            409, "The maximum quantity per product is 10000.", code="quantity_limit"
        )


def add_item(db: Session, user_id: int, product_id: int, quantity: int = 1) -> None:
    product = db.get(Product, product_id)
    if product is None:
        raise StoreError(404, "Product not found.", code="product_not_found")
    cart = container(db, Cart, user_id)
    line = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    target = quantity + (line.quantity if line else 0)
    valid_quantity(product, target)
    if line:
        line.quantity = target
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity))
    cart.updated_at = datetime.now(timezone.utc)
    db.flush()


def add(db: Session, user_id: int, product_id: int, quantity: int) -> CartResponse:
    try:
        lock_customer(db, user_id)
        add_item(db, user_id, product_id, quantity)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return read_cart(db, user_id)


def change(
    db: Session, user_id: int, item_id: int, quantity: int | None
) -> CartResponse:
    try:
        lock_customer(db, user_id)
        line = db.scalar(
            select(CartItem)
            .join(Cart)
            .where(Cart.user_id == user_id, CartItem.id == item_id)
        )
        if line is None:
            raise StoreError(404, "Cart item not found.", code="cart_item_not_found")
        cart = db.get(Cart, line.cart_id)
        if quantity is None:
            db.execute(delete(CartItem).where(CartItem.id == line.id))
        else:
            valid_quantity(db.get(Product, line.product_id), quantity)
            line.quantity = quantity
        cart.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return read_cart(db, user_id)
