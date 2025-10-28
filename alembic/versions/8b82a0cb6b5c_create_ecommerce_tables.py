"""create ecommerce tables

Revision ID: 8b82a0cb6b5c
Revises: 2d2131d3d3b4
Create Date: 2024-05-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "8b82a0cb6b5c"
down_revision: Union[str, None] = "2d2131d3d3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


USER_ROLE_ENUM = sa.Enum("admin", "customer", name="userroleenum")
ORDER_STATUS_ENUM = sa.Enum(
    "created", "paid", "cancelled", "done", name="orderstatus"
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Drop any pre-existing tables from legacy or partial migrations.
    tables_to_drop = [
        "order_items",
        "orders",
        "products_stock",
        "stocks",
        "products",
        "categories",
        "users",
        "sale_item",
        "inventory",
        "sale",
        "product",
        "user",
        "category",
    ]

    for table_name in tables_to_drop:
        if table_name in existing_tables:
            op.drop_table(table_name)

    USER_ROLE_ENUM.create(bind, checkfirst=True)
    ORDER_STATUS_ENUM.create(bind, checkfirst=True)

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=512), nullable=False),
        sa.Column("role", USER_ROLE_ENUM, nullable=False, server_default=sa.text("'customer'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("verification_token", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_verification_token", "users", ["verification_token"], unique=False)

    # Categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    # Products table
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("barcode", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_index("ix_products_barcode", "products", ["barcode"], unique=True)
    op.create_index("ix_products_category_id", "products", ["category_id"], unique=False)

    # Stock locations
    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("location", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_stocks_location", "stocks", ["location"], unique=True)

    # Product stock details
    op.create_table(
        "products_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stocks.id"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("sale_price", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("product_id", "stock_id", name="uq_products_stock_product_stock"),
    )
    op.create_index("ix_products_stock_product_id", "products_stock", ["product_id"], unique=False)
    op.create_index("ix_products_stock_stock_id", "products_stock", ["stock_id"], unique=False)

    # Orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", ORDER_STATUS_ENUM, nullable=False, server_default=sa.text("'created'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)

    # Order items
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price_at_order", sa.Float(), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"], unique=False)


def downgrade() -> None:
    # Drop new order related tables
    op.drop_index("ix_order_items_product_id", table_name="order_items")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_products_stock_stock_id", table_name="products_stock")
    op.drop_index("ix_products_stock_product_id", table_name="products_stock")
    op.drop_table("products_stock")

    op.drop_index("ix_stocks_location", table_name="stocks")
    op.drop_table("stocks")

    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_barcode", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")

    op.drop_index("ix_users_verification_token", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    ORDER_STATUS_ENUM.drop(bind, checkfirst=True)
    USER_ROLE_ENUM.drop(bind, checkfirst=True)

    # Recreate legacy tables to align with the previous schema
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_name", sa.String(length=50), nullable=False),
        sa.Column("category_slug", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("category", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_category_category_name"), ["category_name"], unique=False)
        batch_op.create_index(batch_op.f("ix_category_category_slug"), ["category_slug"], unique=True)
        batch_op.create_index(batch_op.f("ix_category_id"), ["id"], unique=False)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False),
        sa.Column("timezone", sa.String(length=50), nullable=True),
        sa.Column("last_login", sa.TIMESTAMP(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_user_first_name"), ["first_name"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_last_name"), ["last_name"], unique=False)

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("product", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_product_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_product_product_name"), ["product_name"], unique=False)

    op.create_table(
        "sale",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_amount", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("sale", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_sale_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_sale_id"), ["id"], unique=False)

    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("inventory", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_inventory_id"), ["id"], unique=False)

    op.create_table(
        "sale_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price_per_unit", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sale.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("sale_item", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_sale_item_id"), ["id"], unique=False)
