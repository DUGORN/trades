import requests
import subprocess
import time

print("\n" + "=" * 60)
print("   AUTO ASK AI - QUICK ANALYSIS")
print("=" * 60)

# อ่านผลการสแกน
with open('coins.txt', 'r') as f:
    symbols = [line.strip() for line in f if line.strip()]

print("\nTop coins from last scan:")
for i, symbol in enumerate(symbols[:5], 1):
    print(f"  {i}. {symbol}")

symbol = input("\nEnter symbol (e.g., XLMUSDT.P): ").strip().upper()
if not symbol.endswith('.P'):
    symbol += '.P'

# ดึงข้อมูลจาก Binance
try:
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
    
    print(f"\n📊 Data from Binance:")
    print(f"  Symbol: {symbol}")
    print(f"  Price: {current}")
    print(f"  PDH: {pdh}")
    print(f"  PDL: {pdl}")
    print(f"  Low: {low}")
    print(f"  High: {high}")
    
    # สร้างคำถาม
    question = f"""
{symbol} - QUICK ANALYSIS

Current Price: {current}
PDH: {pdh}
PDL: {pdl}
Sweep Low: {low}
Sweep High: {high}
Leverage: 75x
Portfolio: $1000
Risk: 1% ($10)

Note: I will check TradingView for V6, Waterfall, CDV, HTF manually.

Based on price action alone:
- Is price near PDL or PDH?
- Is there a sweep?
- What would be good Entry/SL/TP?

Provide:
Entry: _____
SL: _____
TP1: _____
TP2: _____
"""
    
    print("\n" + "=" * 60)
    print("Question prepared. Opening OpenCode...")
    print("=" * 60)
    
    # เปิด OpenCode
    subprocess.Popen(['opencode'])
    time.sleep(2)
    
    print("\n📋 Copy this to OpenCode:\n")
    print(question)
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print()