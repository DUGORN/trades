import requests

# อ่านจาก coins.txt
with open('coins.txt', 'r') as f:
    symbols = [line.strip() for line in f if line.strip()]

print(f"\nScanning {len(symbols)} coins...\n")

long_setups = []
short_setups = []

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
        low = float(klines[-1][3])
        high = float(klines[-1][2])
        
        # LONG: Sweep Low + Rejection
        if low < pdl and current > pdl:
            long_setups.append({
                'symbol': symbol,
                'price': current,
                'sweep': low
            })
        
        # SHORT: Sweep High + Rejection
        if high > pdh and current < pdh:
            short_setups.append({
                'symbol': symbol,
                'price': current,
                'sweep': high
            })
            
    except:
        pass

print("🟢 LONG SETUPS (Sweep Low + Rejection):")
print("-" * 60)
if long_setups:
    for s in long_setups:
        print(f"  {s['symbol']:15} | Price: {s['price']:>10,.2f} | Sweep: {s['sweep']:,.2f}")
else:
    print("  No LONG setups")

print("\n🔴 SHORT SETUPS (Sweep High + Rejection):")
print("-" * 60)
if short_setups:
    for s in short_setups:
        print(f"  {s['symbol']:15} | Price: {s['price']:>10,.2f} | Sweep: {s['sweep']:,.2f}")
else:
    print("  No SHORT setups")

print(f"\n{'='*60}")
print(f"Total: {len(long_setups)} LONG | {len(short_setups)} SHORT")
print(f"{'='*60}\n")