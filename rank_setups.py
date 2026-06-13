import requests
from datetime import datetime

# อ่านจาก coins.txt
with open('coins.txt', 'r') as f:
    symbols = [line.strip() for line in f if line.strip()]

print(f"\n🔍 Scanning and Ranking {len(symbols)} coins...\n")

setups = []

for symbol in symbols:
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
        volume = float(klines[-1][5])
        
        # คำนวณระยะ
        dist_pdh = abs(current - pdh) / pdh * 100
        dist_pdl = abs(current - pdl) / pdl * 100
        
        # เช็คเงื่อนไข
        is_sweep_low = low < pdl
        is_sweep_high = high > pdh
        is_rejection_low = is_sweep_low and current > pdl
        is_rejection_high = is_sweep_high and current < pdh
        
        # คำนวณคะแนน (0-100)
        score = 0
        
        # 1. คะแนนจาก Distance (0-30 คะแนน)
        if dist_pdl <= 1.5:
            score += 30 - (dist_pdl * 20)  # ใกล้ PDL = คะแนนสูง
        if dist_pdh <= 1.5:
            score += 30 - (dist_pdh * 20)  # ใกล้ PDH = คะแนนสูง
        
        # 2. คะแนนจาก Sweep (0-40 คะแนน)
        if is_sweep_low:
            score += 40
            direction = "LONG"
        elif is_sweep_high:
            score += 40
            direction = "SHORT"
        else:
            direction = "NONE"
        
        # 3. คะแนนจาก Volume (0-20 คะแนน)
        if volume > 1000000:  # Volume สูง
            score += 20
        elif volume > 500000:
            score += 10
        
        # 4. คะแนนจาก Rejection (0-10 คะแนน)
        if is_rejection_low or is_rejection_high:
            score += 10
        
        # เพิ่มข้อมูลใน list
        if score > 0:
            setups.append({
                'symbol': symbol,
                'price': current,
                'score': round(score, 1),
                'direction': direction,
                'distance': min(dist_pdh, dist_pdl),
                'volume': volume
            })
            
    except:
        pass

# เรียงตามคะแนน
setups.sort(key=lambda x: x['score'], reverse=True)

# แสดงผล Top 20
print("=" * 90)
print(f"{'Rank':<6} {'Symbol':<15} {'Score':<8} {'Direction':<10} {'Price':<12} {'Dist%':<8} {'Volume':<15}")
print("=" * 90)

for i, setup in enumerate(setups[:20], 1):
    direction_icon = "🟢 LONG" if setup['direction'] == "LONG" else "🔴 SHORT"
    print(f"{i:<6} {setup['symbol']:<15} {setup['score']:<8} {direction_icon:<10} {setup['price']:<12,.2f} {setup['distance']:<8.2f} {setup['volume']:<15,.0f}")

print("=" * 90)
print(f"\nTotal Setups Found: {len(setups)}")
print(f"\n🏆 Top 3 Recommendations:")
print("=" * 70)
if len(setups) >= 3:
    for i in range(3):
        setup = setups[i]
        direction_icon = "🟢 LONG" if setup['direction'] == "LONG" else "🔴 SHORT" if setup['direction'] == "SHORT" else "⚪ NONE"
        print(f"  {i+1}. {setup['symbol']} (Score: {setup['score']})")
        print(f"     {direction_icon} | Price: {setup['price']} | Dist: {setup['distance']}% | Vol: {setup['volume']}")
        print()
print("=" * 70)