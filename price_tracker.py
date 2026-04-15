import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time
import schedule

# ── settings ──────────────────────────────────────────────────────────────────
PRODUCTS = [
    {
        "name": "boAt Rockerz 450 Bluetooth Headphone",
        "url": "https://www.amazon.in/boAt-Rockerz-450-Bluetooth-Headphone/dp/B07Q3LXKRQ",
    },
    {
        "name": "Logitech M235 Wireless Mouse",
        "url": "https://www.amazon.in/Logitech-910-002201-M235-Wireless-Mouse/dp/B003NR57BY",
    },
]

TARGET_PRICE = 500          # alert if price drops below this (in ₹)
CSV_FILE    = "price_history.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

# ── helpers ───────────────────────────────────────────────────────────────────

def get_price(url: str) -> float | None:
    """Fetch the current price of an Amazon product."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] Could not reach URL: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Amazon stores the price in a few possible spots — try each one
    price_selectors = [
        "span.a-price-whole",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price .a-offscreen",
    ]

    for selector in price_selectors:
        tag = soup.select_one(selector)
        if tag:
            raw = tag.get_text(strip=True)
            # remove ₹, commas, dots at the end  →  "1,299.00" → 1299.0
            cleaned = raw.replace("₹", "").replace(",", "").split(".")[0].strip()
            if cleaned.isdigit():
                return float(cleaned)

    print("  [WARN] Price element not found on page.")
    return None


def save_to_csv(name: str, price: float, url: str) -> None:
    """Append one row to the CSV log."""
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Product Name", "Price (₹)", "URL"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, price, url])


def check_alert(name: str, price: float) -> None:
    """Print an alert if the price is below the target."""
    if price < TARGET_PRICE:
        print(f"  🔔 ALERT! '{name}' is ₹{price} — below your target of ₹{TARGET_PRICE}!")
    else:
        print(f"  ✅ Price is ₹{price} (target: ₹{TARGET_PRICE})")


def load_history() -> list[dict]:
    """Read all rows from the CSV and return as a list of dicts."""
    if not os.path.isfile(CSV_FILE):
        return []

    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

# ── main job ──────────────────────────────────────────────────────────────────

def scrape_all() -> None:
    """Check prices for every product in the list."""
    print(f"\n{'='*55}")
    print(f"  Price check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    for product in PRODUCTS:
        print(f"\n🔍 Checking: {product['name']}")
        price = get_price(product["url"])

        if price is not None:
            save_to_csv(product["name"], price, product["url"])
            check_alert(product["name"], price)
        else:
            print("  [SKIP] Could not get price.")

        time.sleep(2)   # be polite — don't hammer the server

    print("\nDone. Results saved to:", CSV_FILE)


def show_history() -> None:
    """Print the price history table from the CSV."""
    rows = load_history()
    if not rows:
        print("No history yet. Run the tracker first.")
        return

    print(f"\n{'─'*70}")
    print(f"{'Timestamp':<22} {'Product':<35} {'Price':>8}")
    print(f"{'─'*70}")
    for row in rows:
        print(f"{row['Timestamp']:<22} {row['Product Name'][:34]:<35} ₹{row['Price (₹)']:>6}")
    print(f"{'─'*70}")

# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Amazon Price Tracker")
    print("1. Check prices now")
    print("2. Show price history")
    print("3. Start auto-check every 60 minutes")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        scrape_all()

    elif choice == "2":
        show_history()

    elif choice == "3":
        print("\nScheduler started. Press Ctrl+C to stop.")
        scrape_all()                               # run once immediately
        schedule.every(60).minutes.do(scrape_all)
        while True:
            schedule.run_pending()
            time.sleep(30)

    else:
        print("Invalid choice.")
