import json
import os
from datetime import datetime

# ===== MENU OPTIONS =====

ENTRY_PATTERNS = [
    "Sweep Low + Rejection",
    "Sweep High + Rejection",
    "V6 Buy Signal",
    "V6 Sell Signal",
    "Breakout PDH",
    "Breakdown PDL",
    "Hammer Candle",
    "Shooting Star",
    "Bullish Engulfing",
    "Bearish Engulfing",
    "SMT Divergence",
    "Other"
]

EXIT_REASONS = [
    "Hit TP1",
    "Hit TP2",
    "Hit TP3",
    "Hit SL",
    "Manual Close (Profit)",
    "Manual Close (Loss)",
    "Trailing Stop",
    "Time Exit (Held too long)",
    "Other"
]

WIN_REASONS = [
    "Followed plan perfectly",
    "Good entry timing",
    "Strong momentum",
    "Volume confirmation",
    "HTF alignment",
    "Lucky",
    "Other"
]

LOSS_REASONS = [
    "Bad entry timing",
    "Against trend",
    "News event",
    "SL too tight",
    "SL too wide",
    "FOMO entry",
    "No confirmation",
    "Market manipulation",
    "Other"
]

DIRECTIONS = ["LONG", "SHORT"]
RESULTS = ["WIN", "LOSS", "BREAKEVEN"]


def show_menu(title, options):
    print(f"\n{title}")
    print("-" * 40)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print()
    while True:
        choice = input("Select number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(" Invalid! Try again.")


def log_trade():
    print("\n" + "=" * 60)
    print("   📝 LOG NEW TRADE")
    print("=" * 60)
    
    # Symbol
    symbol = input("\nSymbol (e.g., XLMUSDT.P): ").strip().upper()
    if not symbol.endswith('.P'):
        symbol += '.P'
    
    # Direction
    direction = show_menu("Direction:", DIRECTIONS)
    
    # Entry Time
    print("\nEntry Time:")
    entry_date = input("  Date (YYYY-MM-DD, Enter=today): ").strip()
    if not entry_date:
        entry_date = datetime.now().strftime("%Y-%m-%d")
    entry_time = input("  Time (HH:MM, Enter=now): ").strip()
    if not entry_time:
        entry_time = datetime.now().strftime("%H:%M")
    entry_datetime = f"{entry_date} {entry_time}"
    
    # Entry Price
    entry_price = input("\nEntry Price: ").strip()
    
    # Exit Time
    print("\nExit Time:")
    exit_date = input("  Date (YYYY-MM-DD, Enter=today): ").strip()
    if not exit_date:
        exit_date = datetime.now().strftime("%Y-%m-%d")
    exit_time = input("  Time (HH:MM, Enter=now): ").strip()
    if not exit_time:
        exit_time = datetime.now().strftime("%H:%M")
    exit_datetime = f"{exit_date} {exit_time}"
    
    # Exit Price
    exit_price = input("\nExit Price: ").strip()
    
    # Result
    result = show_menu("\nResult:", RESULTS)
    
    # Entry Pattern
    entry_pattern = show_menu("\nEntry Pattern (Why did you enter?):", ENTRY_PATTERNS)
    
    # Exit Reason
    exit_reason = show_menu("\nExit Reason (Why did you exit?):", EXIT_REASONS)
    
    # Win/Loss Reason
    if result == "WIN":
        reason = show_menu("\nWhy did you WIN?", WIN_REASONS)
    elif result == "LOSS":
        reason = show_menu("\nWhy did you LOSE?", LOSS_REASONS)
    else:
        reason = show_menu("\nReason:", WIN_REASONS)
    
    # Profit/Loss
    profit = input("\nProfit/Loss (e.g., +15 or -10, Enter=skip): ").strip()
    
    # Notes
    notes = input("Notes (optional, Enter=skip): ").strip()
    
    # Calculate duration
    try:
        entry_dt = datetime.strptime(entry_datetime, "%Y-%m-%d %H:%M")
        exit_dt = datetime.strptime(exit_datetime, "%Y-%m-%d %H:%M")
        duration = exit_dt - entry_dt
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        duration_str = f"{hours}h {minutes}m"
    except:
        duration_str = "Unknown"
    
    # Save
    trade = {
        'symbol': symbol,
        'direction': direction,
        'entry_datetime': entry_datetime,
        'entry_price': entry_price,
        'exit_datetime': exit_datetime,
        'exit_price': exit_price,
        'duration': duration_str,
        'result': result,
        'entry_pattern': entry_pattern,
        'exit_reason': exit_reason,
        'reason': reason,
        'profit_loss': profit,
        'notes': notes
    }
    
    # Read existing
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
    except:
        trades = []
    
    trades.append(trade)
    
    with open('trades.json', 'w') as f:
        json.dump(trades, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Trade logged!")
    print(f"   Duration: {duration_str}")
    print(f"   Result: {result}")


def show_stats():
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
    except:
        print("\n📊 No trades recorded yet.")
        return
    
    total = len(trades)
    wins = sum(1 for t in trades if t['result'] == 'WIN')
    losses = sum(1 for t in trades if t['result'] == 'LOSS')
    breakeven = sum(1 for t in trades if t['result'] == 'BREAKEVEN')
    win_rate = (wins / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("   📊 TRADING STATISTICS")
    print("=" * 60)
    print(f"Total Trades: {total}")
    print(f"Wins: {wins} ({win_rate:.1f}%)")
    print(f"Losses: {losses} ({100-win_rate:.1f}%)")
    print(f"Breakeven: {breakeven}")
    print("=" * 60)
    
    # Entry pattern stats
    print("\n📈 Entry Patterns:")
    patterns = {}
    for t in trades:
        p = t.get('entry_pattern', 'Unknown')
        patterns[p] = patterns.get(p, 0) + 1
    for p, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {p}: {count}")
    
    # Exit reason stats
    print("\n🚪 Exit Reasons:")
    exits = {}
    for t in trades:
        e = t.get('exit_reason', 'Unknown')
        exits[e] = exits.get(e, 0) + 1
    for e, count in sorted(exits.items(), key=lambda x: x[1], reverse=True):
        print(f"  {e}: {count}")
    
    # Recent trades
    print("\n📝 Recent Trades (Last 5):")
    print("-" * 60)
    for trade in trades[-5:][::-1]:
        icon = "✅" if trade['result'] == 'WIN' else "❌" if trade['result'] == 'LOSS' else "➖"
        print(f"\n  {icon} {trade['symbol']} {trade['direction']}")
        print(f"     Entry: {trade.get('entry_datetime', '?')} @ {trade.get('entry_price', '?')}")
        print(f"     Exit:  {trade.get('exit_datetime', '?')} @ {trade.get('exit_price', '?')}")
        print(f"     Duration: {trade.get('duration', '?')}")
        print(f"     Entry: {trade.get('entry_pattern', '?')}")
        print(f"     Exit:  {trade.get('exit_reason', '?')}")
        print(f"     Reason: {trade.get('reason', '?')}")
        if trade.get('profit_loss'):
            print(f"     P/L: {trade['profit_loss']}")
    
    print("\n" + "=" * 60)


def export_csv():
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
        
        with open('trades.csv', 'w', encoding='utf-8') as f:
            f.write("Date,Symbol,Direction,Entry Time,Entry Price,Exit Time,Exit Price,Duration,Result,Entry Pattern,Exit Reason,Reason,P/L,Notes\n")
            for t in trades:
                f.write(f"{t.get('entry_datetime','')},{t.get('symbol','')},{t.get('direction','')},{t.get('entry_datetime','')},{t.get('entry_price','')},{t.get('exit_datetime','')},{t.get('exit_price','')},{t.get('duration','')},{t.get('result','')},{t.get('entry_pattern','')},{t.get('exit_reason','')},{t.get('reason','')},{t.get('profit_loss','')},{t.get('notes','')}\n")
        
        print("\n✅ Exported to trades.csv")
    except:
        print("\n❌ No data to export")


# ===== MAIN MENU =====

if __name__ == "__main__":
    while True:
        print("\n" + "=" * 60)
        print("   📊 TRADE LOGGER")
        print("=" * 60)
        print()
        print("1. Log new trade")
        print("2. Show statistics")
        print("3. Export to CSV")
        print("0. Back to main menu")
        print()
        
        choice = input("Select (0-3): ").strip()
        
        if choice == '1':
            log_trade()
        elif choice == '2':
            show_stats()
        elif choice == '3':
            export_csv()
        elif choice == '0':
            break
        else:
            print("❌ Invalid choice!")