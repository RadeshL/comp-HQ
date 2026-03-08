import math
import logging
from typing import List, Dict, Optional
from config import settings

logger = logging.getLogger(__name__)

class RankingTool:
    def __init__(self):
        self.rating_weight = 0.4
        self.review_weight = 0.3
        self.price_weight = 0.3
    
    def rank_products(self, products: List[Dict]) -> List[Dict]:
        """Rank products using hybrid scoring algorithm"""
        if not products:
            return []
        
        # Calculate scores for each product
        scored_products = []
        for product in products:
            score = self._calculate_hybrid_score(product)
            product['score'] = score
            scored_products.append(product)
        
        # Sort by score (descending)
        scored_products.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N products
        return scored_products[:settings.TOP_PRODUCTS_COUNT]
    
    def _calculate_hybrid_score(self, product: Dict) -> float:
        """Calculate hybrid score for a product"""
        try:
            # Extract product data
            rating = product.get('rating', 0) or 0
            review_count = product.get('review_count', 0) or 0
            price = product.get('price', 0) or 0
            
            # Calculate individual scores
            rating_score = self._calculate_rating_score(rating)
            review_score = self._calculate_review_score(review_count)
            price_score = self._calculate_price_score(price, self._get_min_price_for_comparison())
            
            # Calculate weighted hybrid score
            hybrid_score = (
                self.rating_weight * rating_score +
                self.review_weight * review_score +
                self.price_weight * price_score
            )
            
            return round(hybrid_score, 3)
            
        except Exception as e:
            logger.error(f"Error calculating score for product: {e}")
            return 0.0
    
    def _calculate_rating_score(self, rating: Optional[float]) -> float:
        """Calculate rating score (normalized to 0-1)"""
        if not rating or rating is None or rating <= 0:
            return 0.0
        
        # Normalize rating to 0-1 scale (assuming 5-star max)
        return min(rating / 5.0, 1.0)
    
    def _calculate_review_score(self, review_count: Optional[int]) -> float:
        """Calculate review score using logarithmic scaling"""
        if not review_count or review_count is None or review_count <= 0:
            return 0.0
        
        # Use logarithmic scaling to give diminishing returns
        # log(1) = 0, log(10) = 1, log(100) = 2, etc.
        log_score = math.log10(review_count)
        
        # Normalize to 0-1 scale (assuming max meaningful reviews around 10,000)
        max_log = math.log10(10000)
        return min(log_score / max_log, 1.0)
    
    def _calculate_price_score(self, price: float, min_price: float) -> float:
        """Calculate price score (lower is better)"""
        if not price or price <= 0 or not min_price or min_price <= 0:
            return 0.0
        
        # Price score: lowest price gets highest score
        # score = min_price / price
        return min(min_price / price, 1.0)
    
    def _get_min_price_for_comparison(self) -> float:
        """Get minimum price for comparison (fallback to 1.0)"""
        return 1.0  # Default minimum price
    
    def rank_products_with_llm(self, products: List[Dict], component_name: str) -> List[Dict]:
        """Rank products using simple rule-based approach (fallback for LLM)"""
        # For now, use the hybrid ranking
        # This can be enhanced later with actual LLM integration
        logger.info(f"Using hybrid ranking for {len(products)} products of {component_name}")
        return self.rank_products(products)
    
    def create_ranking_explanation(self, product: Dict) -> str:
        """Create explanation for why a product was ranked highly"""
        try:
            score = product.get('score', 0)
            rating = product.get('rating', 'N/A')
            reviews = product.get('review_count', 'N/A')
            price = product.get('price', 'N/A')
            seller = product.get('seller', 'Unknown')
            
            explanation = f"Score: {score:.3f}\n"
            explanation += f"Rating: {rating}/5\n"
            explanation += f"Reviews: {reviews}\n"
            explanation += f"Price: ${price}\n"
            explanation += f"Seller: {seller}\n"
            
            # Add reasoning
            if rating and rating >= 4.0:
                explanation += "High customer satisfaction\n"
            
            if reviews and reviews is not None and reviews >= 100:
                explanation += "Well-established product with many reviews\n"
            
            if price and price is not None and price <= 50:
                explanation += "Competitive pricing\n"
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error creating ranking explanation: {e}")
            return f"Score: {product.get('score', 0):.3f}"

class SimpleLLMRanking:
    """Simple fallback ranking that simulates LLM-like reasoning"""
    
    def __init__(self):
        self.ranking_tool = RankingTool()
    
    def rank_with_reasoning(self, products: List[Dict], component_name: str) -> List[Dict]:
        """Rank products with detailed reasoning"""
        ranked_products = self.ranking_tool.rank_products(products)
        
        # Add detailed reasoning for each product
        for i, product in enumerate(ranked_products):
            reasoning = self._generate_reasoning(product, component_name, i + 1)
            product['reasoning'] = reasoning
        
        return ranked_products
    
    def _generate_reasoning(self, product: Dict, component_name: str, rank: int) -> str:
        """Generate human-like reasoning for product ranking"""
        name = product.get('name', 'Unknown')
        price = product.get('price', 0)
        rating = product.get('rating', 0)
        reviews = product.get('review_count', 0)
        seller = product.get('seller', 'Unknown')
        
        reasoning = f"Ranked #{rank}: {name}\n\n"
        
        # Price analysis
        if price is not None and price <= 10:
            reasoning += "💰 Excellent value - very affordable option\n"
        elif price <= 50:
            reasoning += "💰 Good value - reasonably priced\n"
        elif price <= 100:
            reasoning += "💰 Moderate pricing - mid-range option\n"
        else:
            reasoning += "💰 Premium pricing - high-end option\n"
        
        # Rating analysis
        if rating >= 4.5:
            reasoning += "⭐ Outstanding customer satisfaction\n"
        elif rating >= 4.0:
            reasoning += "⭐ Very good customer reviews\n"
        elif rating >= 3.5:
            reasoning += "⭐ Good customer feedback\n"
        elif rating > 0:
            reasoning += "⭐ Mixed customer reviews\n"
        else:
            reasoning += "⭐ No rating data available\n"
        
        # Review count analysis
        if reviews >= 1000:
            reasoning += "📊 Highly popular with extensive reviews\n"
        elif reviews >= 100:
            reasoning += "📊 Well-established product\n"
        elif reviews >= 10:
            reasoning += "📊 Limited but positive feedback\n"
        else:
            reasoning += "📊 New or niche product\n"
        
        # Seller analysis
        if seller.lower() in ['amazon', 'digi-key', 'sparkfun', 'adafruit']:
            reasoning += f"🏪 Trusted seller: {seller}\n"
        else:
            reasoning += f"🏪 Seller: {seller}\n"
        
        # Component-specific recommendations
        if any(keyword in component_name.lower() for keyword in ['arduino', 'esp32', 'raspberry']):
            reasoning += "🔧 Good choice for microcontroller projects\n"
        elif any(keyword in component_name.lower() for keyword in ['sensor', 'ultrasonic', 'temperature']):
            reasoning += "🔧 Suitable for sensor applications\n"
        
        return reasoning
