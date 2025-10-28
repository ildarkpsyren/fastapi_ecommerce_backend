"""Order related endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models import Order, OrderItem, OrderStatus, ProductStock, User, UserRoleEnum
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from app.services.payments import process_payment_placeholder

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[OrderRead], summary="List user orders")
def list_orders(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Order]:
    """List orders belonging to the current user or all orders for admins."""

    if current_user.role == UserRoleEnum.ADMIN:
        return db.query(Order).all()
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED, summary="Create order")
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    """Create a new order for the authenticated user."""

    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain items")
    order = Order(user_id=current_user.id)
    db.add(order)
    for item in payload.items:
        product_stock = db.query(ProductStock).filter(ProductStock.id == item.product_stock_id).first()
        if product_stock is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product stock not found")
        if product_stock.qty < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock for selected product"
            )
        product_stock.qty -= item.quantity
        order_item = OrderItem(
            product_id=product_stock.product_id,
            quantity=item.quantity,
            price_at_order=product_stock.sale_price,
        )
        order.items.append(order_item)
        db.add(product_stock)
    db.commit()
    db.refresh(order)
    process_payment_placeholder(order)
    return order


@router.get("/{order_id}", response_model=OrderRead, summary="Retrieve order")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    """Retrieve an order by identifier. Customers can only access their own orders."""

    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if current_user.role != UserRoleEnum.ADMIN and order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this order")
    return order


@router.patch("/{order_id}/status", response_model=OrderRead, summary="Update order status")
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Order:
    """Allow administrators to update order statuses."""

    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status = payload.status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
