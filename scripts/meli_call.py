"""
Simple Mercado Libre public API caller for quick checks.
Usage:
  - Set environment variables to change behavior (PowerShell syntax shown):
      $env:MLC_SITE = 'MLA'           # default
      $env:MLC_QUERY = 'iphone'       # optional: if set, runs /sites/{site}/search?q={query}

  - Run with the project's Python:
      C:/Users/equipo/AppData/Local/Programs/Python/Python313/python.exe scripts/meli_call.py

Notes:
  - This script uses urllib (stdlib) so no extra deps are required.
  - Authenticated operations (create items, upload images) require OAuth access tokens and are not attempted here.
"""

import os
import sys
import urllib.request
import urllib.parse
import json

PY = sys.executable

API_BASE = 'https://api.mercadolibre.com'

def get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
        'Referer': 'https://www.mercadolibre.com',
        'Connection': 'keep-alive'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        try:
            return json.loads(raw.decode('utf-8'))
        except Exception:
            return raw.decode('utf-8')


def main():
    site = os.environ.get('MLC_SITE', 'MLA')
    query = os.environ.get('MLC_QUERY')

    if query:
        q = urllib.parse.quote_plus(query)
        url = f"{API_BASE}/sites/{site}/search?q={q}"
        print(f"Calling Mercado Libre search: {url}")
        data = get(url)
        # Print a short summary
        results = data.get('results') if isinstance(data, dict) else None
        if isinstance(results, list):
            print(f"Found {len(results)} results (showing up to 5):")
            for idx, item in enumerate(results[:5], 1):
                title = item.get('title')
                price = item.get('price')
                currency = item.get('currency_id')
                permalink = item.get('permalink')
                print(f"{idx}. {title} — {price} {currency} — {permalink}")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    else:
        url = f"{API_BASE}/sites/{site}/categories"
        print(f"Calling Mercado Libre categories: {url}")
        data = get(url)
        if isinstance(data, list):
            print(f"Site {site} has {len(data)} categories. First 10 IDs/names:")
            for cat in data[:10]:
                print(f"- {cat.get('id')}: {cat.get('name')}")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error calling Mercado Libre API:', str(e))
        sys.exit(2)
