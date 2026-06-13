import requests
import sys

symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT.P"
symbol = symbol.upper()

# ลบ .P สำหรับ API
api_symbol = symbol.replace('.P', '')

try:
    # ราคา
    price = requests.get(f'https://fapi.binance.com/fapi/v1/ticker/price?symbol={api_symbol}').json()
    current = float(price['price'])
    
    # ข้อมูล 15m
    klines = requests.get(
        f'https://fapi.binance.com/fapi/v1/klines',
        params={'symbol': api_symbol, 'interval': '15m', 'limit': 50}
    ).json()
    
    current_price = float(klines[-1][4])
    pdh = float(klines[-2][2])
    pdl = float(klines[-2][3])
    high = float(klines[-1][2])
    low = float(klines[-1][3])
    
    print(f"\n{'='*60}")
    print(f"  {symbol} - {current_price:,.2f}")
    print(f"{'='*60}")
    print(f"  PDH: {pdh:,.2f}")
    print(f"  PDL: {pdl:,.2f}")
    print(f"  High: {high:,.2f}")
    print(f"  Low: {low:,.2f}")
    print(f"{'='*60}")
    
    # เช็ค
    if low < pdl:
        print(f"\n  ✅ SWEEP LOW ที่ {low:,.2f}")
    if high > pdh:
        print(f"\n  ✅ SWEEP HIGH ที่ {high:,.2f}")
    
    dist_pdh = abs(current_price - pdh) / pdh * 100
    dist_pdl = abs(current_price - pdl) / pdl * 100
    
    if dist_pdh <= 1.5:
        print(f"\n  📍 Near PDH ({dist_pdh:.2f}%)")
    if dist_pdl <= 1.5:
        print(f"\n  📍 Near PDL ({dist_pdl:.2f}%)")
    
    print(f"\n{'='*60}")
    print(f"  💡 Copy ข้อมูลนี้ไปถาม OpenCode:")
    print(f"  {symbol}")
    print(f"  ราคา: {current_price:,.2f}")
    print(f"  PDH: {pdh:,.2f} | PDL: {pdl:,.2f}")
    print(f"  High: {high:,.2f} | Low: {low:,.2f}")
    print(f"{'='*60}\n")
    
except Exception as e:
    print(f"\n  ❌ Error: {e}\n")