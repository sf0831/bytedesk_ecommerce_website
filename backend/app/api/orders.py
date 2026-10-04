from typing import Annotated

from fastapi import APIRouter, Query

from ..dependencies import CurrentUser, DatabaseSession
from ..schemas.order import CheckoutRequest, OrderDetail, OrderPage
from ..services import order

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("", response_model=OrderPage)
def read(
    db: DatabaseSession,
    user: CurrentUser,
    page: Annotated[int, Query(ge=1, le=2147483647)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return order.list_orders(db, user.id, page, page_size)


@router.post("", response_model=OrderDetail, status_code=201)
def checkout(data: CheckoutRequest, db: DatabaseSession, user: CurrentUser):
    return order.checkout(db, user.id, data)


@router.get("/{order_id}", response_model=OrderDetail)
def read_detail(order_id: int, db: DatabaseSession, user: CurrentUser):
    return order.detail(db, user.id, order_id)
