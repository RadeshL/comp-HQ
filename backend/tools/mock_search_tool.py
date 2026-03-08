import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class MockSearchTool:
    """Mock search tool for testing when real scraping is blocked"""
    
    def __init__(self):
        pass
    
    def search_amazon(self, component_name: str) -> List[Dict]:
        """Mock Amazon search results"""
        return self._get_mock_products(component_name, "Amazon")
    
    def search_digikey(self, component_name: str) -> List[Dict]:
        """Mock Digi-Key search results"""
        return self._get_mock_products(component_name, "Digi-Key")
    
    def search_sparkfun(self, component_name: str) -> List[Dict]:
        """Mock SparkFun search results"""
        return self._get_mock_products(component_name, "SparkFun")
    
    def search_all_sources(self, component_name: str) -> List[Dict]:
        """Search across all mock sources"""
        all_products = []
        
        # Get mock products from each source
        amazon_products = self.search_amazon(component_name)
        digikey_products = self.search_digikey(component_name)
        sparkfun_products = self.search_sparkfun(component_name)
        
        all_products.extend(amazon_products)
        all_products.extend(digikey_products)
        all_products.extend(sparkfun_products)
        
        logger.info(f"Found {len(all_products)} mock products for {component_name}")
        return all_products
    
    def _get_mock_products(self, component_name: str, seller: str) -> List[Dict]:
        """Generate mock products based on component type"""
        
        # Base products for different component types
        if "arduino" in component_name.lower():
            return [
                {
                    'name': f'Arduino Uno R3 - {seller}',
                    'price': 22.99,
                    'seller': seller,
                    'rating': 4.5,
                    'review_count': 1250,
                    'product_link': f'https://example.com/{seller.lower()}/arduino-uno-r3',
                    'source': seller.lower()
                },
                {
                    'name': f'Arduino Uno Starter Kit - {seller}',
                    'price': 45.99,
                    'seller': seller,
                    'rating': 4.7,
                    'review_count': 890,
                    'product_link': f'https://example.com/{seller.lower()}/arduino-uno-starter',
                    'source': seller.lower()
                },
                {
                    'name': f'Arduino Uno WiFi Rev2 - {seller}',
                    'price': 49.99,
                    'seller': seller,
                    'rating': 4.3,
                    'review_count': 450,
                    'product_link': f'https://example.com/{seller.lower()}/arduino-uno-wifi',
                    'source': seller.lower()
                }
            ]
        
        elif "esp32" in component_name.lower():
            return [
                {
                    'name': f'ESP32 DevKit V1 - {seller}',
                    'price': 8.99,
                    'seller': seller,
                    'rating': 4.6,
                    'review_count': 2100,
                    'product_link': f'https://example.com/{seller.lower()}/esp32-devkit',
                    'source': seller.lower()
                },
                {
                    'name': f'ESP32 CAM Module - {seller}',
                    'price': 12.99,
                    'seller': seller,
                    'rating': 4.4,
                    'review_count': 1800,
                    'product_link': f'https://example.com/{seller.lower()}/esp32-cam',
                    'source': seller.lower()
                },
                {
                    'name': f'ESP32-S3 Development Board - {seller}',
                    'price': 15.99,
                    'seller': seller,
                    'rating': 4.2,
                    'review_count': 320,
                    'product_link': f'https://example.com/{seller.lower()}/esp32-s3',
                    'source': seller.lower()
                }
            ]
        
        elif "sensor" in component_name.lower() or "ultrasonic" in component_name.lower():
            return [
                {
                    'name': f'HC-SR04 Ultrasonic Sensor - {seller}',
                    'price': 3.99,
                    'seller': seller,
                    'rating': 4.3,
                    'review_count': 1500,
                    'product_link': f'https://example.com/{seller.lower()}/hc-sr04',
                    'source': seller.lower()
                },
                {
                    'name': f'Ultrasonic Distance Sensor Module - {seller}',
                    'price': 5.99,
                    'seller': seller,
                    'rating': 4.1,
                    'review_count': 890,
                    'product_link': f'https://example.com/{seller.lower()}/ultrasonic-module',
                    'source': seller.lower()
                },
                {
                    'name': f'Waterproof Ultrasonic Sensor - {seller}',
                    'price': 12.99,
                    'seller': seller,
                    'rating': 4.5,
                    'review_count': 450,
                    'product_link': f'https://example.com/{seller.lower()}/waterproof-ultrasonic',
                    'source': seller.lower()
                }
            ]
        
        elif "led" in component_name.lower():
            return [
                {
                    'name': f'LED Strip 5m RGB - {seller}',
                    'price': 18.99,
                    'seller': seller,
                    'rating': 4.4,
                    'review_count': 2300,
                    'product_link': f'https://example.com/{seller.lower()}/led-strip-rgb',
                    'source': seller.lower()
                },
                {
                    'name': f'Addressable LED Strip WS2812B - {seller}',
                    'price': 24.99,
                    'seller': seller,
                    'rating': 4.6,
                    'review_count': 1800,
                    'product_link': f'https://example.com/{seller.lower()}/ws2812b-strip',
                    'source': seller.lower()
                },
                {
                    'name': f'LED Strip Waterproof 12V - {seller}',
                    'price': 15.99,
                    'seller': seller,
                    'rating': 4.2,
                    'review_count': 980,
                    'product_link': f'https://example.com/{seller.lower()}/led-strip-waterproof',
                    'source': seller.lower()
                }
            ]
        
        elif "breadboard" in component_name.lower():
            return [
                {
                    'name': f'Solderless Breadboard 830 Points - {seller}',
                    'price': 7.99,
                    'seller': seller,
                    'rating': 4.5,
                    'review_count': 3400,
                    'product_link': f'https://example.com/{seller.lower()}/breadboard-830',
                    'source': seller.lower()
                },
                {
                    'name': f'Half-size Breadboard 400 Points - {seller}',
                    'price': 4.99,
                    'seller': seller,
                    'rating': 4.3,
                    'review_count': 2100,
                    'product_link': f'https://example.com/{seller.lower()}/breadboard-400',
                    'source': seller.lower()
                },
                {
                    'name': f'Breadboard with Power Supply - {seller}',
                    'price': 12.99,
                    'seller': seller,
                    'rating': 4.7,
                    'review_count': 890,
                    'product_link': f'https://example.com/{seller.lower()}/breadboard-power',
                    'source': seller.lower()
                }
            ]
        
        # Default generic products
        else:
            return [
                {
                    'name': f'{component_name} Basic - {seller}',
                    'price': 9.99,
                    'seller': seller,
                    'rating': 4.0,
                    'review_count': 500,
                    'product_link': f'https://example.com/{seller.lower()}/{component_name.lower().replace(" ", "-")}',
                    'source': seller.lower()
                },
                {
                    'name': f'{component_name} Pro - {seller}',
                    'price': 19.99,
                    'seller': seller,
                    'rating': 4.5,
                    'review_count': 250,
                    'product_link': f'https://example.com/{seller.lower()}/{component_name.lower().replace(" ", "-")}-pro',
                    'source': seller.lower()
                },
                {
                    'name': f'{component_name} Premium - {seller}',
                    'price': 29.99,
                    'seller': seller,
                    'rating': 4.8,
                    'review_count': 100,
                    'product_link': f'https://example.com/{seller.lower()}/{component_name.lower().replace(" ", "-")}-premium',
                    'source': seller.lower()
                }
            ]
