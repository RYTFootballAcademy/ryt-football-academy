"""Fan-shop helper backed by the canonical CRM Product model."""

from sqlalchemy.orm import Session

from ai_agent.crm.models import Product


class FanShop:
    def add_product(self, db: Session, name: str, price: float, stock: int):
        product = Product(name=name, price=float(price), stock=stock)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def list_products(self, db: Session):
        return db.query(Product).order_by(Product.id.desc()).all()

    def update_stock(self, db: Session, product_id: int, stock: int):
        product = db.get(Product, product_id)
        if product:
            product.stock = stock
            db.commit()
            db.refresh(product)
        return product
