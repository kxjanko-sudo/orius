import json
import time
import os
import requests
from datetime import datetime

# ==============================
# CONFIG
# ==============================

CRYPTOS = [
    "BTC", "ETH", "BNB", "SOL",
    "MATIC", "XRP", "DOGE", "ZEC", "SUI"
]

FIAT = "USD"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "prices.json")

last_prices = {}

API_URL = "https://min-api.cryptocompare.com/data/pricemulti"

# ==============================
# LOOP
# ==============================

def fetch_prices():
    global last_prices

    try:
        r = requests.get(API_URL, params={
            "fsyms": ",".join(CRYPTOS),
            "tsyms": FIAT
        }, timeout=10)

        data = r.json()


        out = {}
        for sym in CRYPTOS:
            price = data.get(sym, {}).get(FIAT)
            sym_lower = sym.lower()
            if price:
                old = last_prices.get(sym_lower)
                change = ((price - old) / old) if old else 0
                out[sym_lower] = {"price": price, "change": change}
                last_prices[sym_lower] = price

                print(
                    f"{datetime.now().strftime('%H:%M:%S')} | "
                    f"{sym:5} | {price:,.6f} {FIAT} ({change:+.3%})"
                )

        # Écriture atomique
        tmp = OUTPUT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f)
        os.replace(tmp, OUTPUT_FILE)

    except Exception as e:
        print("❌ Erreur API:", e)


# ==============================
# MAIN LOOP
# ==============================

if __name__ == "__main__":
    print("🟢 CryptoCompare REST polling démarré")

    while True:
        fetch_prices()
        time.sleep(1)  # 1 seconde = quasi temps réel
