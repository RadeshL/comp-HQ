import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Component, Product, ComponentSelection, ComponentCreate, ProductCreate
from tools.intelligent_search_tool import IntelligentSearchTool
from tools.ranking_tool import RankingTool, SimpleLLMRanking
from config import settings

logger = logging.getLogger(__name__)

class ComponentService:
    def __init__(self):
        # Use intelligent search for real web scraping
        self.search_tool = IntelligentSearchTool()
        self.ranking_tool = RankingTool()
        self.llm_ranking = SimpleLLMRanking()
    
    def process_components(self, component_list: List[str], session_id: str) -> Dict:
        """Process a list of components and return initial status"""
        try:
            db = next(get_db())
            
            # Create components in database if they don't exist
            created_components = []
            for component_name in component_list:
                component = self._get_or_create_component(db, component_name)
                created_components.append(component)
            
            return {
                "status": "success",
                "message": f"Processed {len(created_components)} components",
                "components": [{"id": comp.id, "name": comp.name} for comp in created_components],
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing components: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    def get_ranked_products(self, component_name: str, session_id: str) -> Dict:
        """Get top ranked products for a component"""
        try:
            db = next(get_db())
            
            # Get or create component
            component = self._get_or_create_component(db, component_name)
            
            # Use intelligent search to find products across the internet
            logger.info(f"Starting intelligent search for {component_name}")
            search_results = self.search_tool.search_component_internet(component_name)
            
            if not search_results:
                logger.warning(f"No products found for {component_name}")
                return {
                    "status": "no_products",
                    "message": f"No products found for {component_name}",
                    "component_name": component_name,
                    "top_products": []
                }
            
            # Rank products using our ranking algorithm
            logger.info(f"Ranking {len(search_results)} products for {component_name}")
            ranked_products = self.llm_ranking.rank_with_reasoning(search_results, component_name)
            
            # Add component_id, created_at, and id to each product
            for i, product in enumerate(ranked_products):
                product['component_id'] = component.id
                product['created_at'] = datetime.now().isoformat()
                product['id'] = i + 1  # Temporary ID for search results
            
            return {
                "status": "success",
                "component_name": component_name,
                "top_products": ranked_products[:settings.TOP_PRODUCTS_COUNT]
            }
            
        except Exception as e:
            logger.error(f"Error getting ranked products for {component_name}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "component_name": component_name,
                "top_products": []
            }
        finally:
            db.close()
    
    def select_product(self, component_name: str, product_id: int, session_id: str) -> Dict:
        """Save user's product selection"""
        try:
            db = next(get_db())
            
            # Get component
            component = db.query(Component).filter(Component.name == component_name).first()
            if not component:
                return {"status": "error", "message": f"Component {component_name} not found"}
            
            # Get product
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {"status": "error", "message": f"Product {product_id} not found"}
            
            # Check if selection already exists
            existing_selection = db.query(ComponentSelection).filter(
                ComponentSelection.component_id == component.id,
                ComponentSelection.session_id == session_id
            ).first()
            
            if existing_selection:
                # Update existing selection
                existing_selection.product_id = product_id
                message = "Product selection updated"
            else:
                # Create new selection
                selection = ComponentSelection(
                    component_id=component.id,
                    product_id=product_id,
                    session_id=session_id
                )
                db.add(selection)
                message = "Product selection saved"
            
            db.commit()
            
            return {
                "status": "success",
                "message": message,
                "component_name": component_name,
                "product_name": product.name
            }
            
        except Exception as e:
            logger.error(f"Error selecting product: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    def get_session_selections(self, session_id: str) -> List[Dict]:
        """Get all selections for a session"""
        try:
            db = next(get_db())
            
            selections = db.query(ComponentSelection).filter(
                ComponentSelection.session_id == session_id
            ).all()
            
            result = []
            for selection in selections:
                component = selection.component
                product = selection.product
                
                result.append({
                    "component_name": component.name,
                    "product_name": product.name,
                    "price": product.price,
                    "seller": product.seller,
                    "rating": product.rating,
                    "review_count": product.review_count,
                    "product_link": product.product_link
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting session selections: {e}")
            return []
        finally:
            db.close()
    
    def _get_or_create_component(self, db: Session, component_name: str) -> Component:
        """Get existing component or create new one"""
        component = db.query(Component).filter(Component.name == component_name).first()
        if not component:
            component = Component(name=component_name)
            db.add(component)
            db.commit()
            db.refresh(component)
        return component
    
    def _save_product_to_db(self, db: Session, component_id: int, product_data: Dict) -> Product:
        """Save product to database"""
        # Check if product already exists
        existing_product = db.query(Product).filter(
            Product.component_id == component_id,
            Product.name == product_data.get('name', ''),
            Product.seller == product_data.get('seller', ''),
            Product.price == product_data.get('price', 0)
        ).first()
        
        if existing_product:
            # Update existing product
            existing_product.rating = product_data.get('rating')
            existing_product.review_count = product_data.get('review_count')
            existing_product.product_link = product_data.get('product_link')
            existing_product.score = product_data.get('score', 0)
            db.commit()
            db.refresh(existing_product)
            return existing_product
        else:
            # Create new product
            product = Product(
                component_id=component_id,
                name=product_data.get('name', ''),
                price=product_data.get('price', 0),
                seller=product_data.get('seller', ''),
                rating=product_data.get('rating'),
                review_count=product_data.get('review_count'),
                product_link=product_data.get('product_link'),
                score=product_data.get('score', 0)
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            return product
    
    def _convert_products_to_response(self, products: List[Product]) -> List[Dict]:
        """Convert Product objects to response dictionaries"""
        result = []
        for product in products:
            result.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "seller": product.seller,
                "rating": product.rating,
                "review_count": product.review_count,
                "product_link": product.product_link,
                "score": product.score,
                "component_id": product.component_id,
                "created_at": product.created_at.isoformat() if product.created_at else None
            })
        return result
