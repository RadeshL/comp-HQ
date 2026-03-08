from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import Base, get_db

# SQLAlchemy Models
class Component(Base):
    __tablename__ = "components"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="component")
    selections = relationship("ComponentSelection", back_populates="component")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    seller = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    product_link = Column(String, nullable=True)
    score = Column(Float, nullable=True)  # Ranking score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    component = relationship("Component", back_populates="products")
    selections = relationship("ComponentSelection", back_populates="product")

class ComponentSelection(Base):
    __tablename__ = "component_selections"
    
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    session_id = Column(String, index=True, nullable=False)  # To track user sessions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    component = relationship("Component", back_populates="selections")
    product = relationship("Product", back_populates="selections")

# Pydantic Models for API
class ProductBase(BaseModel):
    name: str
    price: float
    seller: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    product_link: Optional[str] = None
    score: Optional[float] = None

class ProductCreate(ProductBase):
    component_id: int

class ProductResponse(ProductBase):
    id: int
    component_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ComponentBase(BaseModel):
    name: str

class ComponentCreate(ComponentBase):
    pass

class ComponentResponse(ComponentBase):
    id: int
    created_at: datetime
    products: List[ProductResponse] = []
    
    class Config:
        from_attributes = True

class ComponentSelectionBase(BaseModel):
    component_id: int
    product_id: int
    session_id: str

class ComponentSelectionCreate(ComponentSelectionBase):
    pass

class ComponentSelectionResponse(ComponentSelectionBase):
    id: int
    created_at: datetime
    component: ComponentResponse
    product: ProductResponse
    
    class Config:
        from_attributes = True

# Request/Response Models for API Endpoints
class ComponentListRequest(BaseModel):
    components: List[str]

class ProductRankingRequest(BaseModel):
    component_name: str
    session_id: str

class ProductRankingResponse(BaseModel):
    component_name: str
    top_products: List[ProductResponse]

class ProductSelectionRequest(BaseModel):
    component_name: str
    product_id: int
    session_id: str

class ReportRequest(BaseModel):
    session_id: str

class ReportResponse(BaseModel):
    message: str
    download_url: Optional[str] = None
