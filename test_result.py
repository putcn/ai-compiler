```python
import os
import requests
from bs4 import BeautifulSoup
import json
import re

product_id = os.environ['PRODUCT_ID']
url = f'https://www.amazon.com/dp/{product_id}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

product_name_element = soup.find('span', {'id': 'productTitle'})
product_name = product_name_element.text.strip() if product_name_element else None

price_whole = soup.find('span', {'class': 'a-price-whole'})
price_fraction = soup.find('span', {'class': 'a-price-fraction'})
price = None
if price_whole and price_fraction:
    price = float(f"{price_whole.text}.{price_fraction.text}")

rating_span = soup.find('span', {'class': 'a-icon-alt'})
rating = None
if rating_span:
    match = re.search(r'(\d+\.\d+) out of 5', rating_span.text)
    if match:
        rating = float(match.group(1))

result = {
    'product_name': product_name,
    'price': price,
    'rating': rating
}

print(json.dumps(result))
```