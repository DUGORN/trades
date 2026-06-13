import requests

print("🔍 กำลังค้นหาเหรียญที่มี Leverage >= 75x...\n")

# ดึงข้อมูล Futures ทั้งหมด
url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
response = requests.get(url)
data = response.json()

# กรองเหรียญที่มี leverage >= 75
high_leverage_coins = []

for symbol in data['symbols']:
    if symbol['quoteAsset'] == 'USDT' and symbol['status'] == 'TRADING':
        # เช็ค leverage
        max_leverage = int(symbol.get('maxLeverage', 0))
        
        if max_leverage >= 75:
            coin_name = symbol['symbol'] + '.P'
            high_leverage_coins.append({
                'symbol': coin_name,
                'leverage': max_leverage
            })

print(f"✅ พบ {len(high_leverage_coins)} เหรียญที่มี Leverage >= 75x\n")

# เรียงตาม leverage
high_leverage_coins.sort(key=lambda x: x['leverage'], reverse=True)

# แสดงผล
print("=" * 70)
print(f"{'Symbol':20} | {'Leverage':10}")
print("=" * 70)

for coin in high_leverage_coins:
    print(f"{coin['symbol']:20} | {coin['leverage']:>5}x")

print("=" * 70)

# อ่านเหรียญที่มีอยู่
try:
    with open('coins.txt', 'r') as f:
        existing = set(line.strip() for line in f if line.strip())
except:
    existing = set()

# หาเหรียญใหม่
new_coins = [c for c in high_leverage_coins if c['symbol'] not in existing]

print(f"\n📋 คุณมีอยู่แล้ว: {len(existing)} เหรียญ")
print(f"➕ จะเพิ่ม: {len(new_coins)} เหรียญ")

if new_coins:
    print("\n" + "=" * 70)
    choice = input("ต้องการเพิ่มเหรียญเหล่านี้ไหม? (y/n): ").lower()
    
    if choice == 'y':
        # เพิ่มลงในไฟล์
        with open('coins.txt', 'a') as f:
            for coin in new_coins:
                f.write(f"\n{coin['symbol']}")
        
        print(f"\n✅ เพิ่ม {len(new_coins)} เหรียญสำเร็จ!")
        print("\nเหรียญที่เพิ่ม:")
        for coin in new_coins[:10]:
            print(f"  - {coin['symbol']} ({coin['leverage']}x)")
        if len(new_coins) > 10:
            print(f"  ... และอีก {len(new_coins) - 10} เหรียญ")

print()