# ai_agent/modules/fan_shop.py
from sqlalchemy import Column, Integer, String, Float
from ai_agent.modules.database import Base
from sqlalchemy.orm import Session

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)

class FanShop:
    def add_product(self, db: Session, name: str, price: float, stock: int):
        product = Product(name=name, price=price, stock=stock)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def list_products(self, db: Session):
        return db.query(Product).all()

    def update_stock(self, db: Session, product_id: int, stock: int):
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.stock = stock
            db.commit()
            db.refresh(product)
        return product
