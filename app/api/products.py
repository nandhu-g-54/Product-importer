from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# GET ALL PRODUCTS
# ----------------------------
@router.get("/", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
    search: str | None = Query(None, description="Search by sku or name")
):
    query = db.query(Product)

    if search:
        query = query.filter(
            (Product.sku.ilike(f"%{search}%")) |
            (Product.name.ilike(f"%{search}%"))
        )

    products = query.offset(offset).limit(limit).all()
    return products


# ----------------------------
# CREATE PRODUCT
# ----------------------------
@router.post("/", response_model=ProductResponse)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    exists = db.query(Product).filter(Product.sku == data.sku).first()
    if exists:
        raise HTTPException(status_code=400, detail="SKU already exists")

    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ----------------------------
# UPDATE PRODUCT
# ----------------------------
@router.put("/{sku}", response_model=ProductResponse)
def update_product(sku: str, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# ----------------------------
# DELETE A PRODUCT
# ----------------------------
@router.delete("/{sku}")
def delete_product(sku: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


# ----------------------------
# BULK DELETE
# ----------------------------
@router.delete("/")
def bulk_delete(db: Session = Depends(get_db)):
    db.query(Product).delete()
    db.commit()
    return {"message": "All products deleted..!"}
