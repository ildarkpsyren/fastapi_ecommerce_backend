"""Database models for stock locations and product stock levels."""
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Stock(Base):
    """Represents a warehouse or stock location."""

    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    product_stocks: Mapped[list["ProductStock"]] = relationship(
        "ProductStock", back_populates="stock", cascade="all, delete-orphan"
    )


class ProductStock(Base):
    """Associative table storing per-stock product details."""

    __tablename__ = "products_stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, default=0)
    sale_price: Mapped[float] = mapped_column(Float, default=0.0)

    product: Mapped["Product"] = relationship("Product", back_populates="stocks")
    stock: Mapped[Stock] = relationship("Stock", back_populates="product_stocks")
