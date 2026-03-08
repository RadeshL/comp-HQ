import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Optional
import logging
import time
from config import settings

logger = logging.getLogger(__name__)

class ScraperTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })
    
    def get_detailed_product_info(self, product_url: str, source: str) -> Dict:
        """Scrape detailed product information from a product page"""
        if not product_url:
            return {}
        
        try:
            response = self.session.get(product_url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            if source == 'amazon':
                return self._scrape_amazon_product(response.content, product_url)
            elif source == 'digikey':
                return self._scrape_digikey_product(response.content, product_url)
            elif source == 'sparkfun':
                return self._scrape_sparkfun_product(response.content, product_url)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error scraping product details from {source}: {e}")
            return {}
    
    def _scrape_amazon_product(self, html_content: bytes, product_url: str) -> Dict:
        """Scrape detailed product information from Amazon product page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract product title
            title_elem = soup.find('span', id='productTitle')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract price
            price_elem = soup.find('span', class_='a-price-whole')
            price_fraction_elem = soup.find('span', class_='a-price-fraction')
            price = self._extract_price(
                f"{price_elem.get_text() if price_elem else ''}"
                f".{price_fraction_elem.get_text() if price_fraction_elem else '00'}"
            )
            
            # Extract rating
            rating_elem = soup.find('span', class_='a-icon-alt')
            rating = self._extract_rating(rating_elem.get_text() if rating_elem else None)
            
            # Extract review count
            reviews_elem = soup.find('span', id='acrCustomerReviewText')
            review_count = self._extract_review_count(reviews_elem.get_text() if reviews_elem else None)
            
            # Extract seller/brand
            brand_elem = soup.find('a', id='bylineInfo')
            seller = brand_elem.get_text(strip=True) if brand_elem else "Amazon"
            
            # Extract product description
            description_elem = soup.find('div', id='productDescription')
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            return {
                'name': title,
                'price': price,
                'seller': seller,
                'rating': rating,
                'review_count': review_count,
                'product_link': product_url,
                'description': description,
                'source': 'amazon'
            }
            
        except Exception as e:
            logger.error(f"Error scraping Amazon product: {e}")
            return {}
    
    def _scrape_digikey_product(self, html_content: bytes, product_url: str) -> Dict:
        """Scrape detailed product information from Digi-Key product page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract product title
            title_elem = soup.find('h1', class_='product-title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract price
            price_elem = soup.find('span', class_='product-price')
            price = self._extract_price(price_elem.get_text(strip=True) if price_elem else "0")
            
            # Extract manufacturer
            manufacturer_elem = soup.find('span', class_='manufacturer-name')
            seller = manufacturer_elem.get_text(strip=True) if manufacturer_elem else "Unknown"
            
            # Extract description
            description_elem = soup.find('div', class_='product-description')
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract specifications
            specs_elem = soup.find('div', class_='product-specs')
            specifications = specs_elem.get_text(strip=True) if specs_elem else ""
            
            return {
                'name': title,
                'price': price,
                'seller': seller,
                'rating': None,
                'review_count': None,
                'product_link': product_url,
                'description': description,
                'specifications': specifications,
                'source': 'digikey'
            }
            
        except Exception as e:
            logger.error(f"Error scraping Digi-Key product: {e}")
            return {}
    
    def _scrape_sparkfun_product(self, html_content: bytes, product_url: str) -> Dict:
        """Scrape detailed product information from SparkFun product page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract product title
            title_elem = soup.find('h1', class_='product-title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract price
            price_elem = soup.find('span', class_='product-price')
            price = self._extract_price(price_elem.get_text(strip=True) if price_elem else "0")
            
            # Extract description
            description_elem = soup.find('div', class_='product-description')
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract specifications
            specs_elem = soup.find('div', class_='product-specifications')
            specifications = specs_elem.get_text(strip=True) if specs_elem else ""
            
            return {
                'name': title,
                'price': price,
                'seller': 'SparkFun',
                'rating': None,
                'review_count': None,
                'product_link': product_url,
                'description': description,
                'specifications': specifications,
                'source': 'sparkfun'
            }
            
        except Exception as e:
            logger.error(f"Error scraping SparkFun product: {e}")
            return {}
    
    def extract_product_images(self, product_url: str, source: str) -> list:
        """Extract product images from a product page"""
        if not product_url:
            return []
        
        try:
            response = self.session.get(product_url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            images = []
            
            if source == 'amazon':
                img_elems = soup.find_all('img', id='landingImage')
                for img in img_elems:
                    if img.get('src'):
                        images.append(img.get('src'))
            elif source == 'digikey':
                img_elems = soup.find_all('img', class_='product-image')
                for img in img_elems:
                    if img.get('src'):
                        images.append(urljoin(product_url, img.get('src')))
            elif source == 'sparkfun':
                img_elems = soup.find_all('img', class_='product-image')
                for img in img_elems:
                    if img.get('src'):
                        images.append(urljoin(product_url, img.get('src')))
            
            return images[:5]  # Return first 5 images
            
        except Exception as e:
            logger.error(f"Error extracting images from {source}: {e}")
            return []
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from price text"""
        try:
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
            match = re.search(r'[\d,]+', review_text.replace(',', ''))
            return int(match.group(0)) if match else None
        except:
            return None
