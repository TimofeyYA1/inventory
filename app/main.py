from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
import database, db_models, schemas, crud
from database import SessionLocal, engine

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/categories/", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

@app.post("/products/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)

@app.get("/products/filter/", response_model=list[schemas.ProductOut])
def get_products_by_filters(min_price: float = None, max_price: float = None ,category: int  = None, db: Session = Depends(get_db)):
    return crud.get_products_filtered(db, min_price, max_price,category)

@app.patch("/products/{product_id}/", response_model=schemas.ProductOut)
def update_product(product_id: int,product_update: schemas.ProductUpdate,db: Session = Depends(get_db)):
    return crud.update_product(db, product_id, product_update)

@app.get("/products/{product_id}/", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return crud.get_product_by_id(db, product_id)

@app.get("/categories/{category_id}/", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return crud.get_category_by_id(db, category_id)

@app.get("/categories/", response_model=list[schemas.CategoryOut])
def get_all_categories(db: Session = Depends(get_db)):
    return crud.get_all_categories(db)  

@app.delete("/products/{product_id}/")
def remove_product(product_id: int, db: Session = Depends(get_db)):
    return crud.delete_product(db, product_id)

@app.delete("/categories/{category_id}/")
def remove_category(category_id: int,force: bool = Query(False, description="Удалить категорию вместе с продуктами"),db: Session = Depends(get_db)):
    return crud.delete_category(db, category_id, force)