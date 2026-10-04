from datetime import datetime, timezone
from decimal import Decimal
from math import ceil

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from ..models import Cart, CartItem, Order, OrderItem, Product
from ..schemas.order import CheckoutRequest, OrderDetail, OrderPage
from .cart import lock_customer, totals, valid_quantity
from .errors import StoreError


def detail(db: Session, user_id: int, order_id: int) -> Order:
    order = db.scalar(
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items))
    )
    if order is None:
        raise StoreError(404, "Order not found.", code="order_not_found")
    return order


def list_orders(db: Session, user_id: int, page: int, page_size: int) -> OrderPage:
    total = db.scalar(
        select(func.count()).select_from(Order).where(Order.user_id == user_id)
    )
    orders = db.scalars(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .options(selectinload(Order.items))
    )
    return OrderPage(
        items=list(orders),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size),
    )


def checkout(db: Session, user_id: int, data: CheckoutRequest) -> OrderDetail:
    try:
        lock_customer(db, user_id)
        previous = db.scalar(
            select(Order)
            .where(Order.user_id == user_id, Order.checkout_key == data.checkout_key)
            .options(selectinload(Order.items))
        )
        if previous:
            result = OrderDetail.model_validate(previous)
            db.commit()
            return result
        cart = db.scalar(select(Cart).where(Cart.user_id == user_id))
        lines = (
            list(
                db.scalars(
                    select(CartItem)
                    .where(CartItem.cart_id == cart.id)
                    .order_by(CartItem.product_id)
                )
            )
            if cart
            else []
        )
        if not lines:
            raise StoreError(
                409,
                "Your cart is empty. Add a product before checking out.",
                code="empty_cart",
            )
        # Lock inventory in product ID order to avoid overselling and deadlocks.
        products = {
            p.id: p
            for p in db.scalars(
                select(Product)
                .where(Product.id.in_([line.product_id for line in lines]))
                .order_by(Product.id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        }
        for line in lines:
            product = products.get(line.product_id)
            if product is None:
                raise StoreError(
                    409,
                    "A product is no longer available. Please review your cart.",
                    code="product_unavailable",
                )
            valid_quantity(product, line.quantity)
        subtotal = sum(
            (products[line.product_id].price * line.quantity for line in lines),
            Decimal("0.00"),
        )
        (shipping, total) = totals(subtotal)
        now = datetime.now(timezone.utc)
        order = Order(
            user_id=user_id,
            status="pending",
            subtotal=subtotal,
            shipping=shipping,
            total=total,
            created_at=now,
            updated_at=now,
            **data.model_dump(),
        )
        db.add(order)
        db.flush()
        for line in lines:
            product = products[line.product_id]
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=line.quantity,
                    subtotal=product.price * line.quantity,
                )
            )
            product.stock_quantity -= line.quantity
            product.updated_at = now
        db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        cart.updated_at = now
        db.flush()
        result = OrderDetail.model_validate(detail(db, user_id, order.id))
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
