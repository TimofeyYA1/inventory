from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    pass

class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int
    description: str
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

class ProductUpdate(BaseModel):
    name: str = None
    price: float = None
    quantity: int = None
    description: str = None
    category_id: int = None