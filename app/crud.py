from sqlalchemy.orm import Session
import db_models, schemas
from sqlalchemy import and_ ,exc    
from fastapi import HTTPException, status
def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = db_models.Category(**category.model_dump())
    print(category)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def create_product(db: Session, product: schemas.ProductCreate):
    category = db.query(db_models.Category).filter_by(id=product.category_id).first()
    if not category:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "Такой категории не существует,вы можете создать ее сами")
    existing_product = db.query(db_models.Product).filter(db_models.Product.name == product.name,db_models.Product.category_id == product.category_id).first()
    if existing_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Товар с таким именем уже существует в этой категории")
    db_product = db_models.Product(name=product.name,price=product.price,quantity=product.quantity,description=product.description,category_id=product.category_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products_filtered(db: Session,min_price: float = None,max_price: float = None,category: int = None):
    query = db.query(db_models.Product)
    filters = []
    if min_price is not None:
        filters.append(db_models.Product.price >= min_price)
    if max_price is not None:
        filters.append(db_models.Product.price <= max_price)
    if category is not None:
        filters.append(db_models.Product.category_id == category)

    if filters:
        query = query.filter(and_(*filters))
    return query.all()

def update_product(db: Session,product_id: int,product_update: schemas.ProductUpdate):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Продукт не найден")

    if product_update.category_id is not None:
        new_category = db.query(db_models.Category).filter(db_models.Category.id == product_update.category_id).first()
        if not new_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Указанная категория не существует")

    if product_update.name is not None or product_update.category_id is not None:
        new_name = product_update.name if product_update.name is not None else db_product.name
        new_category_id = product_update.category_id if product_update.category_id is not None else db_product.category_id
        
        existing_product = db.query(db_models.Product).filter(db_models.Product.name == new_name,db_models.Product.category_id == new_category_id,db_models.Product.id != product_id).first()
        
        if existing_product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Товар с таким именем уже существует в выбранной категории")

        for field, value in product_update.model_dump(exclude_unset=True).items():
            setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_id(db: Session, product_id: int):
    product = db.query(db_models.Product).filter(db_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Продукт с ID {product_id} не найден")
    return product

def get_category_by_id(db: Session, category_id: int):
    category = db.query(db_models.Category).filter(db_models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Категория с ID {category_id} не найдена")
    return category

def get_all_categories(db: Session):
    return db.query(db_models.Category).all()   

def delete_product(db: Session, product_id: int):
    product = db.query(db_models.Product).filter(db_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Продукт с ID {product_id} не найден")
    
    try:
        db.delete(product)
        db.commit()
        return {"message": f"Продукт с ID {product_id} успешно удален"}
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Ошибка при удалении продукта: {str(e)}")

def delete_category(db: Session, category_id: int, force: bool = False):
    category = db.query(db_models.Category).filter(db_models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Категория с ID {category_id} не найдена")
    
    products = db.query(db_models.Product).filter(db_models.Product.category_id == category_id).all()
    
    if products and not force:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail={"message": "Категория содержит продукты","products_count": len(products),"hint": "Используйте force для удаления с продуктами"})
    
    try:
        if force and products:
            for product in products:
                db.delete(product)
        
        db.delete(category)
        db.commit()
        
        return {
            "message": f"Категория с ID {category_id} успешно удалена",
            "deleted_products_count": len(products) if force else 0
        }
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении: {str(e)}"
        )