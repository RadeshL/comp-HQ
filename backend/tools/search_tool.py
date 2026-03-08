import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
from typing import List, Dict, Optional
import time
import logging
from config import settings

logger = logging.getLogger(__name__)

class SearchTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })
    
    def search_amazon(self, component_name: str) -> List[Dict]:
        """Search for products on Amazon"""
        try:
            search_url = f"https://www.amazon.com/s?k={quote_plus(component_name)}"
            response = self.session.get(search_url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Extract product information from Amazon search results
            product_elements = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for element in product_elements[:10]:  # Limit to first 10 results
                try:
                    name_elem = element.find('h2', class_='a-size-mini')
                    price_elem = element.find('span', class_='a-price-whole')
                    rating_elem = element.find('span', class_='a-icon-alt')
                    reviews_elem = element.find('span', class_='a-size-base')
                    link_elem = element.find('h2', class_='a-size-mini').find('a') if name_elem else None
                    
                    if name_elem and price_elem:
                        product = {
                            'name': name_elem.get_text(strip=True),
                            'price': self._extract_price(price_elem.get_text(strip=True)),
                            'seller': 'Amazon',
                            'rating': self._extract_rating(rating_elem.get_text() if rating_elem else None),
                            'review_count': self._extract_review_count(reviews_elem.get_text() if reviews_elem else None),
                            'product_link': urljoin('https://www.amazon.com', link_elem.get('href')) if link_elem else None,
                            'source': 'amazon'
                        }
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Amazon product: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return []
    
    def search_digikey(self, component_name: str) -> List[Dict]:
        """Search for products on Digi-Key"""
        try:
            search_url = f"https://www.digikey.com/en/products/result?keywords={quote_plus(component_name)}"
            response = self.session.get(search_url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Extract product information from Digi-Key search results
            product_rows = soup.find_all('tr', class_='product-row')
            
            for row in product_rows[:10]:  # Limit to first 10 results
                try:
                    name_elem = row.find('div', class_='product-description')
                    price_elem = row.find('span', class_='product-price')
                    manufacturer_elem = row.find('span', class_='manufacturer')
                    link_elem = row.find('a', class_='product-link')
                    
                    if name_elem and price_elem:
                        product = {
                            'name': name_elem.get_text(strip=True),
                            'price': self._extract_price(price_elem.get_text(strip=True)),
                            'seller': 'Digi-Key',
                            'rating': None,  # Digi-Key doesn't typically show ratings
                            'review_count': None,
                            'product_link': urljoin('https://www.digikey.com', link_elem.get('href')) if link_elem else None,
                            'source': 'digikey'
                        }
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Digi-Key product: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            logger.error(f"Error searching Digi-Key: {e}")
            return []
    
    def search_sparkfun(self, component_name: str) -> List[Dict]:
        """Search for products on SparkFun"""
        try:
            search_url = f"https://www.sparkfun.com/search/results?term={quote_plus(component_name)}"
            response = self.session.get(search_url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Extract product information from SparkFun search results
            product_items = soup.find_all('div', class_='product-listing')
            
            for item in product_items[:10]:  # Limit to first 10 results
                try:
                    name_elem = item.find('h3', class_='product-name')
                    price_elem = item.find('span', class_='product-price')
                    link_elem = item.find('a', class_='product-link')
                    
                    if name_elem and price_elem:
                        product = {
                            'name': name_elem.get_text(strip=True),
                            'price': self._extract_price(price_elem.get_text(strip=True)),
                            'seller': 'SparkFun',
                            'rating': None,
                            'review_count': None,
                            'product_link': urljoin('https://www.sparkfun.com', link_elem.get('href')) if link_elem else None,
                            'source': 'sparkfun'
                        }
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing SparkFun product: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            logger.error(f"Error searching SparkFun: {e}")
            return []
    
    def search_all_sources(self, component_name: str) -> List[Dict]:
        """Search across all configured sources"""
        all_products = []
        
        # Search each source with a small delay to be respectful
        sources = [
            (self.search_amazon, "Amazon"),
            (self.search_digikey, "Digi-Key"),
            (self.search_sparkfun, "SparkFun")
        ]
        
        for search_func, source_name in sources:
            try:
                products = search_func(component_name)
                all_products.extend(products)
                logger.info(f"Found {len(products)} products from {source_name}")
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error searching {source_name}: {e}")
                continue
        
        return all_products
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from price text"""
        try:
            # Remove currency symbols and convert to float
            import re
            price_clean = re.sub(r'[^\d.]', '', price_text)
            return float(price_clean) if price_clean else 0.0
        except:
            return 0.0
    
    def _extract_rating(self, rating_text: Optional[str]) -> Optional[float]:
        """Extract numeric rating from rating text"""
        try:
            if not rating_text:
                return None
            import re
            # Look for pattern like "4.5 out of 5 stars"
            match = re.search(r'(\d+\.?\d*)', rating_text)
            return float(match.group(1)) if match else None
        except:
            return None
    
    def _extract_review_count(self, review_text: Optional[str]) -> Optional[int]:
        """Extract numeric review count from review text"""
        try:
            if not review_text:
                return None
            import re
            # Look for numbers in text like "(1,234) ratings"
            match = re.search(r'[\d,]+', review_text.replace(',', ''))
            return int(match.group(0)) if match else None
        except:
            return None
