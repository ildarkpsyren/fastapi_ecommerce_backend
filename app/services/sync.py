"""Mock external API synchronisation helpers."""
from collections.abc import Iterable
from typing import Dict

from sqlalchemy.orm import Session

from app.models import ProductStock

EXTERNAL_MOCK_DATA: Dict[int, Dict[str, float]] = {
    # product_stock_id: {"qty": int, "sale_price": float}
    1: {"qty": 15, "sale_price": 19.99},
    2: {"qty": 3, "sale_price": 5.49},
}


def sync_product_stock_from_external_api(db: Session, product_stock_ids: Iterable[int]) -> list[ProductStock]:
    """Update price and quantity from the mocked external API."""

    updated_records: list[ProductStock] = []
    for stock_id in product_stock_ids:
        payload = EXTERNAL_MOCK_DATA.get(stock_id)
        if payload is None:
            continue
        product_stock = db.query(ProductStock).filter(ProductStock.id == stock_id).first()
        if product_stock is None:
            continue
        product_stock.qty = int(payload["qty"])
        product_stock.sale_price = float(payload["sale_price"])
        db.add(product_stock)
        updated_records.append(product_stock)
    if updated_records:
        db.commit()
        for record in updated_records:
            db.refresh(record)
    return updated_records
