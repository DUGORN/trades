import requests

# อ่านจาก coins.txt
with open('coins.txt', 'r') as f:
    symbols = [line.strip() for line in f if line.strip()]

print(f"\n{'Symbol':15} | {'Price':12} | {'PDH':12} | {'PDL':12}")
print("-" * 65)

for symbol in symbols:
    try:
        # ลบ .P สำหรับ API
        api_symbol = symbol.replace('.P', '')
        
        klines = requests.get(
            'https://fapi.binance.com/fapi/v1/klines',
            params={'symbol': api_symbol, 'interval': '15m', 'limit': 50}
        ).json()
        
        current = float(klines[-1][4])
        pdh = float(klines[-2][2])
        pdl = float(klines[-2][3])
        
        print(f"{symbol:15} | {current:12,.2f} | {pdh:12,.2f} | {pdl:12,.2f}")
    except:
        pass

print("-" * 65)
print(f"Total: {len(symbols)} coins\n")