import re
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import quote, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class IntelligentSearchTool:

    def __init__(self):

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        self.retailer_search_pages = {
            "sparkfun": "https://www.sparkfun.com/search/results?term={}",
            "adafruit": "https://www.adafruit.com/search?q={}",
            "digikey": "https://www.digikey.com/en/products/result?keywords={}",
            "mouser": "https://www.mouser.com/c/?q={}",
            "banggood": "https://www.banggood.com/search/{}.html",
        }

        self.allowed_domains = [
            "amazon.",
            "digikey.",
            "mouser.",
            "sparkfun.",
            "adafruit.",
            "banggood.",
            "aliexpress.",
            "ebay."
        ]

    # ----------------------------------------------------------
    # MAIN ENTRY
    # ----------------------------------------------------------

    def search_component_internet(self, component_name: str) -> List[Dict]:

        logger.info(f"Searching products for component: {component_name}")

        products = []

        retailer_products = self._scrape_retailer_search_pages(component_name)
        products.extend(retailer_products)

        search_products = self._search_and_scrape(component_name)
        products.extend(search_products)

        unique = {}
        for p in products:
            if p and "product_link" in p:
                unique[p["product_link"]] = p

        products = list(unique.values())

        logger.info(f"Total products collected: {len(products)}")

        return products

    # ----------------------------------------------------------
    # RETAILER SEARCH SCRAPING
    # ----------------------------------------------------------

    def _scrape_retailer_search_pages(self, component: str) -> List[Dict]:

        results = []

        query = quote(component)

        with ThreadPoolExecutor(max_workers=5) as executor:

            futures = []

            for retailer, url_template in self.retailer_search_pages.items():

                url = url_template.format(query)

                futures.append(
                    executor.submit(
                        self._scrape_retailer_page,
                        retailer,
                        url,
                        component
                    )
                )

            for f in as_completed(futures):

                try:
                    data = f.result()
                    if data:
                        results.extend(data)
                except Exception as e:
                    logger.warning(f"Retailer scraping failed: {e}")

        return results

    def _scrape_retailer_page(self, retailer: str, url: str, component: str):

        logger.info(f"Scraping retailer search page: {url}")

        products = []

        try:

            response = requests.get(url, headers=self.headers, timeout=15)

            soup = BeautifulSoup(response.text, "html.parser")

            product_cards = soup.find_all("a", href=True)

            for card in product_cards[:80]:

                title = card.get_text(strip=True)

                if not title:
                    continue

                if not self._fuzzy_match(component, title):
                    continue

                link = card["href"]

                if not link.startswith("http"):
                    parsed = urlparse(url)
                    link = f"{parsed.scheme}://{parsed.netloc}{link}"

                price = self._extract_price(card.get_text())

                products.append(
                    {
                        "name": title[:200],
                        "price": price,
                        "rating": None,
                        "review_count": None,
                        "seller": retailer.capitalize(),
                        "product_link": link,
                    }
                )

        except Exception as e:
            logger.warning(f"{retailer} scraping error: {e}")

        return products

    # ----------------------------------------------------------
    # INTERNET SEARCH (SUPPLEMENTAL)
    # ----------------------------------------------------------

    def _search_and_scrape(self, component: str) -> List[Dict]:

        queries = [
            f"{component} electronics component",
            f"{component} buy online",
            f"{component} module electronics",
            f"{component} development board",
        ]

        urls = []

        with DDGS() as ddgs:

            for query in queries:

                logger.info(f"Running search query: {query}")

                try:

                    results = ddgs.text(query, max_results=10)

                    for r in results:

                        logger.info(f"Search result raw: {r}")

                        url = r.get("href") or r.get("url") or r.get("link")

                        if not url:
                            continue

                        if not self._is_retailer_url(url):
                            continue

                        urls.append(url)

                except Exception as e:
                    logger.warning(f"Search failed for {query}: {e}")

        urls = list(set(urls))[:20]

        products = []

        with ThreadPoolExecutor(max_workers=8) as executor:

            futures = [executor.submit(self._scrape_product_page, u) for u in urls]

            for f in as_completed(futures):

                try:
                    p = f.result()
                    if p:
                        products.append(p)
                except:
                    pass

        return products

    # ----------------------------------------------------------
    # PRODUCT PAGE SCRAPER
    # ----------------------------------------------------------

    def _scrape_product_page(self, url: str) -> Optional[Dict]:

        try:

            response = requests.get(url, headers=self.headers, timeout=15)

            soup = BeautifulSoup(response.text, "html.parser")

            name = self._extract_product_name(soup)

            if not name:
                return None

            price = self._extract_price(soup.get_text())
            rating = self._extract_rating(soup)
            review_count = self._extract_reviews(soup)

            return {
                "name": name,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "seller": self._extract_seller(url),
                "product_link": url,
            }

        except Exception as e:
            logger.warning(f"Product scrape failed: {url} {e}")
            return None

    # ----------------------------------------------------------
    # EXTRACTION
    # ----------------------------------------------------------

    def _extract_product_name(self, soup):

        og = soup.find("meta", property="og:title")

        if og:
            return og.get("content")

        h1 = soup.find("h1")

        if h1:
            return h1.get_text(strip=True)

        return None

    def _extract_price(self, text):

        if not text:
            return None

        match = re.search(r"(\d+\.?\d*)", text)

        if match and match.group(1):
            try:
                return float(match.group(1))
            except:
                return None

        return None

    def _extract_rating(self, soup):

        scripts = soup.find_all("script", type="application/ld+json")

        for s in scripts:

            match = re.search(r'"ratingValue"\s*:\s*"?(\\d+\\.?\\d*)', s.text)

            if match and match.group(1):
                try:
                    return float(match.group(1))
                except:
                    pass

        return None

    def _extract_reviews(self, soup):

        scripts = soup.find_all("script", type="application/ld+json")

        for s in scripts:

            match = re.search(r'"reviewCount"\s*:\s*"?(\\d+)', s.text)

            if match:
                try:
                    return int(match.group(1))
                except:
                    pass

        return None

    # ----------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------

    def _extract_seller(self, url):

        domain = urlparse(url).netloc.replace("www.", "")

        return domain.split(".")[0].capitalize()

    def _is_retailer_url(self, url):

        domain = urlparse(url).netloc.lower()

        for d in self.allowed_domains:
            if d in domain:
                return True

        return False

    # ----------------------------------------------------------
    # FIXED FUZZY MATCH
    # ----------------------------------------------------------

    def _fuzzy_match(self, component, title):

        if not component or not title:
            return False

        component = str(component).lower()
        title = str(title).lower()

        if component in title:
            return True

        words = component.split()

        if not words:
            return False

        matches = sum(1 for w in words if w and w in title)

        threshold = max(1, len(words) // 2)

        return matches >= threshold