# 🛒 Amazon Price Tracker

A simple Python script that tracks product prices on Amazon India and alerts you when prices drop.

## What it does
- Scrapes live prices from Amazon product pages
- Saves price history to a CSV file with timestamps
- Alerts you when price drops below your target
- Can run automatically every 60 minutes

## Setup

```bash
pip install -r requirements.txt
python price_tracker.py
```

## How to add your own products
Open `price_tracker.py` and edit the `PRODUCTS` list:

```python
PRODUCTS = [
    {
        "name": "Your Product Name",
        "url": "https://www.amazon.in/dp/PRODUCT_ID",
    },
]
```

Also set your target price:
```python
TARGET_PRICE = 999  # alert if price drops below ₹999
```

## Output
- `price_history.csv` — all price records with timestamps

## Libraries used
- `requests` — to fetch web pages
- `beautifulsoup4` — to parse HTML and extract price
- `schedule` — to run checks automatically
