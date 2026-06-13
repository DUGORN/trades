import requests

# อ่านจาก coins.txt
with open('coins.txt', 'r') as f:
    symbols = [line.strip() for line in f if line.strip()]

print(f"\nScanning {len(symbols)} coins...\n")

long_setups = []
short_setups = []
wait_setups = []

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
        
        # คำนวณระยะ
        dist_pdh = abs(current - pdh) / pdh * 100
        dist_pdl = abs(current - pdl) / pdl * 100
        
        # เช็คเงื่อนไข
        is_sweep_low = low < pdl
        is_sweep_high = high > pdh
        is_rejection_low = is_sweep_low and current > pdl
        is_rejection_high = is_sweep_high and current < pdh
        is_near_pdh = dist_pdh <= 1.5
        is_near_pdl = dist_pdl <= 1.5
        
        # LONG: ต้อง sweep low + rejection + near PDL
        if is_rejection_low and is_near_pdl:
            long_setups.append({
                'symbol': symbol,
                'price': current,
                'sweep': low,
                'distance': dist_pdl
            })
        
        # SHORT: ต้อง sweep high + rejection + near PDH
        elif is_rejection_high and is_near_pdh:
            short_setups.append({
                'symbol': symbol,
                'price': current,
                'sweep': high,
                'distance': dist_pdh
            })
        
        # ถ้ามี sweep แต่ไม่ผ่านเงื่อนไข = WAIT
        elif is_sweep_low or is_sweep_high:
            wait_setups.append({
                'symbol': symbol,
                'price': current,
                'reason': 'Distance filter failed'
            })
            
    except:
        pass

print("🟢 LONG SETUPS (Sweep Low + Rejection + Near PDL):")
print("-" * 70)
if long_setups:
    for s in long_setups:
        print(f"  {s['symbol']:15} | Price: {s['price']:>10,.2f} | Sweep: {s['sweep']:,.2f} | Dist: {s['distance']:.2f}%")
else:
    print("  No LONG setups")

print("\n SHORT SETUPS (Sweep High + Rejection + Near PDH):")
print("-" * 70)
if short_setups:
    for s in short_setups:
        print(f"  {s['symbol']:15} | Price: {s['price']:>10,.2f} | Sweep: {s['sweep']:,.2f} | Dist: {s['distance']:.2f}%")
else:
    print("  No SHORT setups")

print("\n⏳ WAIT (มี sweep แต่ distance ไกลเกิน 1.5%):")
print("-" * 70)
if wait_setups:
    for s in wait_setups:
        print(f"  {s['symbol']:15} | Price: {s['price']:>10,.2f} | {s['reason']}")
else:
    print("  No WAIT setups")

print(f"\n{'='*70}")
print(f"Total: {len(long_setups)} LONG | {len(short_setups)} SHORT | {len(wait_setups)} WAIT")
print(f"{'='*70}\n")