# from bs4 import BeautifulSoup
# import requests
# import urllib
# query = input("Enter the search query: ")
# query = urllib.parse.quote(query)

# url = f"https://html.duckduckgo.com/html/?q={query}"
# headers = {"User-Agent": "Mozilla/5.0"}
# response = requests.get(url, headers=headers)
# soup = BeautifulSoup(response.text, "html.parser")
# results = soup.find_all("a", class_="result__a")
# print(len(results))
# for result in results:
#     title = result.text
#     link = result["href"]
#     print(f"Title: {title}\nLink: {link}\n")

import requests
import re
import time
from bs4 import BeautifulSoup
from ddgs import DDGS

query = input("Enter the search query: ")

# ecommerce sites we care about
allowed_sites = ["amazon", "flipkart", "ebay", "banggood", "aliexpress", "walmart"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

price_pattern = re.compile(r"[$₹€]\s?\d+(?:,\d{3})*(?:\.\d{2})?")

# STEP 1 — Search the web
with DDGS() as ddgs:
    results = list(ddgs.text(query, max_results=20))

print("\n--- FILTERED PRODUCT PAGES ---\n")

# STEP 2 — filter ecommerce websites
filtered_results = []

for r in results:
    url = r["href"]

    if any(site in url.lower() for site in allowed_sites):
        filtered_results.append(r)

# STEP 3 — visit each page
for res in filtered_results:

    url = res["href"]
    print("Visiting:", url)

    try:
        resp = requests.get(url, headers=headers, timeout=6)
    except:
        print("Skipping (request failed)\n")
        continue

    soup = BeautifulSoup(resp.text, "html.parser")

    prices = []

    # STEP 4 — extract price text
    for text in soup.find_all(string=True):

        # ignore scripts and styles
        if text.parent.name in ["script", "style"]:
            continue

        text = text.strip()

        if len(text) > 20:
            continue

        if price_pattern.search(text):
            prices.append(text)

    if prices:
        print("Found price:", prices[0])
    else:
        print("No price detected")

    print()
    
    # STEP 5 — polite delay (avoid getting blocked)
    time.sleep(1)