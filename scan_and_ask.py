import requests
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def scan_coins():
    try:
        with open('coins.txt', 'r') as f:
            symbols = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("\n❌ coins.txt not found!")
        return []

    setups = []
    for symbol in symbols:
        try:
            api_symbol = symbol.replace('.P', '')
            klines = requests.get(
                'https://fapi.binance.com/fapi/v1/klines',
                params={'symbol': api_symbol, 'interval': '15m', 'limit': 50},
                timeout=10
            ).json()
            
            current = float(klines[-1][4])
            pdh = float(klines[-2][2])
            pdl = float(klines[-2][3])
            low = float(klines[-1][3])
            high = float(klines[-1][2])
            volume = float(klines[-1][5])
            
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
            
            if score > 0:
                setups.append({
                    'symbol': symbol,
                    'price': current,
                    'score': round(score, 1),
                    'direction': direction,
                    'distance': min(dist_pdh, dist_pdl),
                    'volume': volume,
                    'pdh': pdh,
                    'pdl': pdl,
                    'low': low,
                    'high': high
                })
        except Exception as e:
            pass
            
    setups.sort(key=lambda x: x['score'], reverse=True)
    return setups

def show_setups(setups):
    print("\n" + "=" * 90)
    print(f"{'Rank':<6} {'Symbol':<15} {'Score':<8} {'Dir':<8} {'Price':<12} {'Dist%':<8} {'Volume':<15}")
    print("=" * 90)
    
    for i, setup in enumerate(setups[:15], 1):
        dir_icon = "LONG" if setup['direction'] == "LONG" else "SHORT" if setup['direction'] == "SHORT" else "NONE"
        print(f"{i:<6} {setup['symbol']:<15} {setup['score']:<8} {dir_icon:<8} {setup['price']:<12,.2f} {setup['distance']:<8.2f} {setup['volume']:<15,.0f}")
    
    print("=" * 90)
    print(f"\nTotal: {len(setups)} setups found\n")

def ask_ai(setup):
    clear_screen()
    
    print("\n" + "=" * 60)
    print(f"   🎯 COIN SELECTED: {setup['symbol']}")
    print("=" * 60)
    
    print(f"\n📋 COPY THIS TO OPENCODE:\n")
    print("-" * 60)
    print(f"""
{setup['symbol']} - MANDATORY PRICE LEVELS

Current Price: {setup['price']}
Leverage: 75x
Portfolio: $1000
Risk per trade: 1% ($10)

DATA FROM BINANCE:
- PDH: {setup['pdh']}
- PDL: {setup['pdl']}
- Sweep Low: {setup['low']}
- Sweep High: {setup['high']}
- Distance: {setup['distance']:.2f}%

YOU NEED TO CHECK TRADINGVIEW:
- V6: [BUY/SELL]
- Waterfall: [COLD/HOT]
- CDV: [RISING/FALLING]
- HTF Bias: [BULLISH/BEARISH/NEUTRAL]
- Gaussian: [BULL/BEAR]

REQUIRED OUTPUT:
Entry (within 0.3% of current price)
SL (max 1% from Entry)
TP1 (1-2% above/below Entry)
TP2 (2-3% above/below Entry)
Risk:Reward ratio
Position Size

Format:
Entry: _____
SL: _____
TP1: _____
TP2: _____
R:R = _____
Position Size: $_____
""")
    print("-" * 60)
    
    print("\n✅ NOW:")
    print("   1. Copy question above")
    print("   2. Open new PowerShell → Type 'opencode'")
    print("   3. Paste question + Add TradingView data")
    print("   4. Get answer from AI")
    print()
    print("   ⏳ Take your time...")
    print()
    
    input("   Press Enter when you're DONE...")

def main():
    print("\nStarting Scan & Ask AI...")
    time.sleep(1)
    
    clear_screen()
    print("=" * 60)
    print("   SCAN & ASK AI - WORKFLOW")
    print("=" * 60)
    print()
    print("Scanning for setups...")
    
    setups = scan_coins()
    
    if not setups:
        print("\n❌ No setups found!")
        print("Press Enter to exit...")
        input()
        return
    
    show_setups(setups)
    
    print("Options:")
    print("  1-15: Select coin number to analyze")
    print("  q:    Quit")
    print()
    
    choice = input("Select: ").strip().lower()
    
    if choice == 'q':
        print("\nGoodbye!\n")
        return
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(setups):
            ask_ai(setups[idx])
        else:
            print("\n❌ Invalid selection!")
            print("Press Enter to exit...")
            input()
    else:
        print("\n❌ Invalid choice!")
        print("Press Enter to exit...")
        input()

if __name__ == "__main__":
    main()