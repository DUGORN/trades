import requests

def get_price_change(symbol, interval='1d'):
    """ดึงข้อมูลการเปลี่ยนแปลงราคา"""
    try:
        klines = requests.get(
            'https://fapi.binance.com/fapi/v1/klines',
            params={'symbol': symbol, 'interval': interval, 'limit': 2}
        ).json()
        
        if len(klines) < 2:
            return 0
        
        old_price = float(klines[0][4])
        new_price = float(klines[1][4])
        
        return ((new_price - old_price) / old_price) * 100
    except:
        return 0

def scan_and_rank(sort_by='score'):
    with open('coins.txt', 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]

    print(f"\n🔍 Scanning {len(symbols)} coins...\n")

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
            
            # ดึงข้อมูลเปลี่ยนแปลงราคา
            change_1m = get_price_change(api_symbol, '1m')
            change_15m = get_price_change(api_symbol, '15m')
            change_1h = get_price_change(api_symbol, '1h')
            change_4h = get_price_change(api_symbol, '4h')
            change_1d = get_price_change(api_symbol, '1d')
            change_1w = get_price_change(api_symbol, '1w')
            
            dist_pdh = abs(current - pdh) / pdh * 100
            dist_pdl = abs(current - pdl) / pdl * 100
            
            is_sweep_low = low < pdl and current > pdl
            is_sweep_high = high > pdh and current < pdh
            
            score = 0
            direction = "NONE"
            
            if dist_pdl <= 1.5:
                score += 30 - (dist_pdl * 20)
            if dist_pdh <= 1.5:
                score += 30 - (dist_pdh * 20)
                
            if is_sweep_low:
                score += 40
                direction = "LONG"
            elif is_sweep_high:
                score += 40
                direction = "SHORT"
                
            if volume > 1000000:
                score += 20
            elif volume > 500000:
                score += 10
                
            if is_sweep_low or is_sweep_high:
                score += 10
            
            setups.append({
                'symbol': symbol,
                'price': current,
                'score': round(score, 1),
                'direction': direction,
                'distance': min(dist_pdh, dist_pdl),
                'volume': volume,
                'change_1m': change_1m,
                'change_15m': change_15m,
                'change_1h': change_1h,
                'change_4h': change_4h,
                'change_1d': change_1d,
                'change_1w': change_1w,
            })
        except:
            pass

    # เรียงตามที่ต้องการ
    if sort_by == 'score':
        setups.sort(key=lambda x: x['score'], reverse=True)
    elif sort_by == 'volume':
        setups.sort(key=lambda x: x['volume'], reverse=True)
    elif sort_by == 'name':
        setups.sort(key=lambda x: x['symbol'])
    elif sort_by == 'price':
        setups.sort(key=lambda x: x['price'])
    elif sort_by == 'change_1m':
        setups.sort(key=lambda x: x['change_1m'], reverse=True)
    elif sort_by == 'change_15m':
        setups.sort(key=lambda x: x['change_15m'], reverse=True)
    elif sort_by == 'change_1h':
        setups.sort(key=lambda x: x['change_1h'], reverse=True)
    elif sort_by == 'change_4h':
        setups.sort(key=lambda x: x['change_4h'], reverse=True)
    elif sort_by == 'change_1d':
        setups.sort(key=lambda x: x['change_1d'], reverse=True)
    elif sort_by == 'change_1w':
        setups.sort(key=lambda x: x['change_1w'], reverse=True)

    # แสดงผล
    print("=" * 110)
    print(f"{'Rank':<6} {'Symbol':<15} {'Score':<8} {'Dir':<8} {'Price':<12} {'Vol':<12} {'1m':<8} {'15m':<8} {'1h':<8} {'4h':<8} {'1d':<8} {'1w':<8}")
    print("=" * 110)

    limit = input("แสดงกี่เหรียญ? (Enter = ทั้งหมด): ").strip()
    limit = int(limit) if limit else len(setups)

    for i, setup in enumerate(setups[:limit], 1):
        dir_icon = "🟢LONG" if setup['direction'] == "LONG" else "🔴SHORT" if setup['direction'] == "SHORT" else "⚪NONE"
        print(f"{i:<6} {setup['symbol']:<15} {setup['score']:<8} {dir_icon:<8} {setup['price']:<12,.2f} {setup['volume']:<12,.0f} {setup['change_1m']:<+8.2f}% {setup['change_15m']:<+8.2f}% {setup['change_1h']:<+8.2f}% {setup['change_4h']:<+8.2f}% {setup['change_1d']:<+8.2f}% {setup['change_1w']:<+8.2f}%")

    print("=" * 110)
    print(f"\nTotal: {len(setups)} coins\n")

def menu():
    while True:
        print("\n" + "=" * 60)
        print("   CUSTOM RANKING MENU")
        print("=" * 60)
        print()
        print("1. Sort by Score (Default)")
        print("2. Sort by Volume (24h)")
        print("3. Sort by Name (A-Z)")
        print("4. Sort by Price (Low-High)")
        print("5. Sort by Change 1m")
        print("6. Sort by Change 15m")
        print("7. Sort by Change 1h")
        print("8. Sort by Change 4h")
        print("9. Sort by Change 1d")
        print("10. Sort by Change 1w")
        print("0. Back to Main Menu")
        print()
        
        choice = input("Select (0-10): ").strip()
        
        sort_options = {
            '1': 'score',
            '2': 'volume',
            '3': 'name',
            '4': 'price',
            '5': 'change_1m',
            '6': 'change_15m',
            '7': 'change_1h',
            '8': 'change_4h',
            '9': 'change_1d',
            '10': 'change_1w'
        }
        
        if choice == '0':
            break
        elif choice in sort_options:
            scan_and_rank(sort_options[choice])
            input("\nPress Enter to continue...")
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    menu()