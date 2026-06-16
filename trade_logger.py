#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trade Logger Pro - บันทึกและวิเคราะห์ผลการเทรดแบบมืออาชีพ
รองรับการกรอกแบบ Coin Quantity และคำนวณ USDT อัตโนมัติ
"""

import json
import os
import csv
from datetime import datetime

TRADES_FILE = "trades.json"

# ==========================================
# OPTIONS FOR DROPDOWN
# ==========================================
ENTRY_PATTERNS = [
    "Shark", "SMT", "V6", "Box", "OB Target", 
    "Banker Yellow", "RSI Divergence", "HTF Pattern",
    "Engulfing", "Pin Bar", "Other", "Unknown"
]

EXIT_REASONS = [
    "TP1", "TP2", "TP3", "SL", "BE (Breakeven)", 
    "Trailing Stop", "Manual", "Time Exit", 
    "Reversal Signal", "Other"
]

MARKET_SESSIONS = ["Asia", "London", "New York", "Overlap", "Unknown"]
TREND_DIRECTIONS = ["Bull", "Bear", "Sideway", "Unknown"]
VOLATILITY_LEVELS = ["Low", "Medium", "High", "Unknown"]
EMOTION_LEVELS = ["Calm", "Confident", "Anxious", "Fearful", "Greedy", "FOMO", "Unknown"]
MISTAKE_TYPES = ["None", "FOMO", "Revenge Trade", "Overtrade", "Early Entry", "Late Exit", "No SL", "Moved SL", "Other"]
TIMEFRAMES = ["1m", "5m", "15m", "30m", "1H", "4H", "D", "W"]

def load_trades():
    """โหลด trades จากไฟล์ JSON"""
    if not os.path.exists(TRADES_FILE):
        return []
    try:
        with open(TRADES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_trades(trades):
    """บันทึก trades ลงไฟล์ JSON"""
    with open(TRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(trades, f, indent=2, ensure_ascii=False)

def select_from_list(prompt, options):
    """แสดงเมนูเลือกจาก list"""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = int(input(f"Select (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a number")

def input_yes_no(prompt):
    """รับค่า Yes/No"""
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ['y', 'yes']:
            return True
        elif ans in ['n', 'no']:
            return False
        print("❌ Please enter y or n")

def calculate_duration(entry_time, exit_time):
    """คำนวณระยะเวลา"""
    try:
        t1 = datetime.strptime(entry_time, "%Y-%m-%d %H:%M")
        t2 = datetime.strptime(exit_time, "%Y-%m-%d %H:%M")
        delta = t2 - t1
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "Unknown"

def log_trade():
    """บันทึก trade ใหม่แบบละเอียด"""
    print("\n" + "="*60)
    print("   📝 LOG NEW TRADE")
    print("="*60)
    
    # ===== หมวด 1: ข้อมูลพื้นฐาน =====
    print("\n📋 [1/6] BASIC INFORMATION")
    print("-" * 60)
    
    pair = input("Pair (e.g., BTCUSDT.P): ").strip().upper()
    if not pair:
        print("❌ Pair is required!")
        return
    
    side = input("Side (LONG/SHORT): ").strip().upper()
    if side not in ["LONG", "SHORT"]:
        print("❌ Side must be LONG or SHORT")
        return
    
    while True:
        try:
            entry_price = float(input("Entry Price: "))
            if entry_price > 0:
                break
            print("❌ Price must be greater than 0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    while True:
        try:
            exit_price = float(input("Exit Price: "))
            if exit_price > 0:
                break
            print("❌ Price must be greater than 0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    entry_time = input("Entry Time (YYYY-MM-DD HH:MM): ").strip()
    exit_time = input("Exit Time (YYYY-MM-DD HH:MM): ").strip()
    
    # คำนวณ P/L
    if side == "LONG":
        pnl = (exit_price - entry_price)
    else:
        pnl = (entry_price - exit_price)
    pnl_percentage = (pnl / entry_price) * 100 if entry_price > 0 else 0
    
    # ===== หมวด 2: Entry Details =====
    print("\n🎯 [2/6] ENTRY DETAILS")
    print("-" * 60)
    
    entry_pattern = select_from_list("Entry Pattern:", ENTRY_PATTERNS)
    entry_timeframe = select_from_list("Entry Timeframe:", TIMEFRAMES)
    
    # Confluence
    print("\nConfluence Signals (เลือกได้หลายอัน, พิมพ์ 0 เมื่อจบ):")
    confluence_list = []
    confluence_options = ["Shark", "SMT", "V6", "Box", "Gaussian", "Teeth", 
                         "Banker", "RSI Div", "CDV", "HTF Pattern", "OB/FVG"]
    while True:
        conf = select_from_list("Add confluence (0 to finish):", 
                               ["0. Done"] + [f"{i+1}. {c}" for i, c in enumerate(confluence_options)])
        if conf == "0. Done":
            break
        confluence_list.append(conf.split(". ")[1])
    
    has_sweep = input_yes_no("Liquidity Sweep before entry?")
    
    # ===== หมวด 3: Market Context =====
    print("\n📈 [3/6] MARKET CONTEXT")
    print("-" * 60)
    
    session = select_from_list("Market Session:", MARKET_SESSIONS)
    trend = select_from_list("Trend Direction:", TREND_DIRECTIONS)
    volatility = select_from_list("Volatility:", VOLATILITY_LEVELS)
    htf_bias = select_from_list("HTF Bias (1H/4H):", ["Bull", "Bear", "Neutral", "Unknown"])
    news_event = input("News Event (FOMC/NFP/None): ").strip() or "None"
    
    # ===== หมวด 4: Risk Management =====
    print("\n🛡️  [4/6] RISK MANAGEMENT")
    print("-" * 60)
    
    # ถามว่าจะกรอกแบบไหน
    print("\nPosition Size Type:")
    print("  1. USDT (กรอกเป็น USDT)")
    print("  2. Coin Quantity (กรอกเป็นจำนวนเหรียญ)")
    
    while True:
        try:
            size_type = int(input("Select (1-2): "))
            if size_type in [1, 2]:
                break
            print("❌ Please select 1 or 2")
        except ValueError:
            print("❌ Please enter a number")
    
    coin_quantity = 0
    
    if size_type == 1:
        # กรอกเป็น USDT
        while True:
            try:
                position_size = float(input("Position Size (USDT): "))
                if position_size > 0:
                    break
                print("❌ Must be greater than 0")
            except ValueError:
                print("❌ Please enter a valid number")
        coin_quantity = position_size / entry_price if entry_price > 0 else 0
    
    else:
        # กรอกเป็นจำนวนเหรียญ
        coin_name = pair.replace('.P', '').replace('USDT', '')
        while True:
            try:
                coin_quantity = float(input(f"Quantity ({coin_name}): "))
                if coin_quantity > 0:
                    break
                print("❌ Must be greater than 0")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # คำนวณเป็น USDT อัตโนมัติ
        position_size = coin_quantity * entry_price
        print(f"\n   ✅ Calculated Position Size: {position_size:.2f} USDT")
        print(f"   ({coin_quantity} {coin_name} × {entry_price})")
    
    while True:
        try:
            leverage = int(input("Leverage (e.g., 75): "))
            if leverage > 0:
                break
            print("❌ Must be greater than 0")
        except ValueError:
            print("❌ Please enter a number")
    
    while True:
        try:
            risk_percent = float(input("Risk % of Portfolio: "))
            break
        except ValueError:
            print("❌ Please enter a number")
    
    sl_price = input("SL Price (or skip): ").strip()
    tp_price = input("TP Price (or skip): ").strip()
    
    # คำนวณ R:R
    rr_ratio = "N/A"
    try:
        if sl_price and tp_price:
            sl_dist = abs(entry_price - float(sl_price))
            tp_dist = abs(float(tp_price) - entry_price)
            if sl_dist > 0:
                rr_ratio = f"1:{tp_dist/sl_dist:.1f}"
    except:
        pass
    
    # ===== หมวด 5: Exit Details =====
    print("\n🚪 [5/6] EXIT DETAILS")
    print("-" * 60)
    
    exit_reason = select_from_list("Exit Reason:", EXIT_REASONS)
    exit_pattern = select_from_list("Exit Pattern (if any):", 
                                   ["None"] + ENTRY_PATTERNS)
    exit_timeframe = select_from_list("Exit Timeframe:", TIMEFRAMES)
    partial_close = input_yes_no("Partial close?")
    
    # ===== หมวด 6: Psychology & Learning =====
    print("\n🧠 [6/6] PSYCHOLOGY & LEARNING")
    print("-" * 60)
    
    emotion_before = select_from_list("Emotion BEFORE entry:", EMOTION_LEVELS)
    emotion_during = select_from_list("Emotion DURING trade:", EMOTION_LEVELS)
    emotion_after = select_from_list("Emotion AFTER exit:", EMOTION_LEVELS)
    
    followed_plan = input_yes_no("Followed trading plan?")
    mistake = select_from_list("Mistake made:", MISTAKE_TYPES)
    lesson = input("Lesson learned: ").strip() or "None"
    screenshot = input("Screenshot link/path (optional): ").strip() or "None"
    notes = input("Additional notes: ").strip() or "None"
    
    # ===== บันทึกข้อมูล =====
    duration = calculate_duration(entry_time, exit_time)
    
    trade = {
        # Basic
        "pair": pair,
        "side": side,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "entry_time": entry_time,
        "exit_time": exit_time,
        "duration": duration,
        "pnl": round(pnl, 2),
        "pnl_percentage": round(pnl_percentage, 2),
        "coin_quantity": round(coin_quantity, 4),
        
        # Entry Details
        "entry_pattern": entry_pattern,
        "entry_timeframe": entry_timeframe,
        "confluence_count": len(confluence_list),
        "confluence_list": confluence_list,
        "has_sweep": has_sweep,
        
        # Market Context
        "session": session,
        "trend": trend,
        "volatility": volatility,
        "htf_bias": htf_bias,
        "news_event": news_event,
        
        # Risk Management
        "position_size": round(position_size, 2),
        "leverage": leverage,
        "risk_percent": risk_percent,
        "sl_price": sl_price or "N/A",
        "tp_price": tp_price or "N/A",
        "rr_ratio": rr_ratio,
        
        # Exit Details
        "exit_reason": exit_reason,
        "exit_pattern": exit_pattern,
        "exit_timeframe": exit_timeframe,
        "partial_close": partial_close,
        
        # Psychology
        "emotion_before": emotion_before,
        "emotion_during": emotion_during,
        "emotion_after": emotion_after,
        "followed_plan": followed_plan,
        "mistake": mistake,
        "lesson": lesson,
        "screenshot": screenshot,
        "notes": notes,
        
        # Metadata
        "timestamp": datetime.now().isoformat()
    }
    
    trades = load_trades()
    trades.append(trade)
    save_trades(trades)
    
    print("\n" + "="*60)
    print("✅ Trade logged successfully!")
    print(f"   Pair: {pair} {side}")
    print(f"   Entry: {entry_price} → Exit: {exit_price}")
    print(f"   Quantity: {coin_quantity} {coin_name}")
    print(f"   Position Size: {position_size:.2f} USDT")
    print(f"   P/L: ${pnl:.2f} ({pnl_percentage:.2f}%)")
    print(f"   R:R: {rr_ratio}")
    print(f"   Pattern: {entry_pattern} ({len(confluence_list)} confluences)")
    print("="*60)

def show_statistics():
    """แสดงสถิติแบบละเอียด"""
    trades = load_trades()
    
    if not trades:
        print("\n📭 No trades recorded yet.")
        return
    
    total = len(trades)
    wins = [t for t in trades if t.get("pnl", 0) > 0]
    losses = [t for t in trades if t.get("pnl", 0) < 0]
    breakeven = [t for t in trades if t.get("pnl", 0) == 0]
    
    win_rate = (len(wins) / total * 100) if total > 0 else 0
    
    total_pnl = sum(t.get("pnl", 0) for t in trades)
    avg_win = sum(t.get("pnl", 0) for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t.get("pnl", 0) for t in losses) / len(losses) if losses else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    print("\n" + "="*60)
    print("   📊 TRADING STATISTICS")
    print("="*60)
    
    # Overall Performance
    print(f"\n📈 Overall Performance:")
    print(f"   Total Trades: {total}")
    print(f"   ✅ Wins: {len(wins)} ({win_rate:.1f}%)")
    print(f"   ❌ Losses: {len(losses)} ({len(losses)/total*100:.1f}%)")
    print(f"   💰 Total P/L: ${total_pnl:.2f}")
    print(f"   📊 Profit Factor: {profit_factor:.2f}")
    
    # Analysis by Pattern
    print("\n🎯 Performance by Entry Pattern:")
    print("-" * 60)
    patterns = {}
    for t in trades:
        p = t.get("entry_pattern", "Unknown")
        if p not in patterns:
            patterns[p] = {"trades": 0, "wins": 0, "pnl": 0}
        patterns[p]["trades"] += 1
        if t.get("pnl", 0) > 0:
            patterns[p]["wins"] += 1
        patterns[p]["pnl"] += t.get("pnl", 0)
    
    for p, data in sorted(patterns.items(), key=lambda x: x[1]["pnl"], reverse=True):
        wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
        print(f"   {p:15} | {data['trades']:2} trades | WR: {wr:5.1f}% | P/L: ${data['pnl']:+7.2f}")
    
    # Analysis by Session
    print("\n🌍 Performance by Session:")
    print("-" * 60)
    sessions = {}
    for t in trades:
        s = t.get("session", "Unknown")
        if s not in sessions:
            sessions[s] = {"trades": 0, "wins": 0, "pnl": 0}
        sessions[s]["trades"] += 1
        if t.get("pnl", 0) > 0:
            sessions[s]["wins"] += 1
        sessions[s]["pnl"] += t.get("pnl", 0)
    
    for s, data in sorted(sessions.items(), key=lambda x: x[1]["pnl"], reverse=True):
        wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
        print(f"   {s:10} | {data['trades']:2} trades | WR: {wr:5.1f}% | P/L: ${data['pnl']:+7.2f}")
    
    # Analysis by Emotion
    print("\n🧠 Performance by Emotion (Before Entry):")
    print("-" * 60)
    emotions = {}
    for t in trades:
        e = t.get("emotion_before", "Unknown")
        if e not in emotions:
            emotions[e] = {"trades": 0, "wins": 0, "pnl": 0}
        emotions[e]["trades"] += 1
        if t.get("pnl", 0) > 0:
            emotions[e]["wins"] += 1
        emotions[e]["pnl"] += t.get("pnl", 0)
    
    for e, data in sorted(emotions.items(), key=lambda x: x[1]["pnl"], reverse=True):
        wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
        print(f"   {e:12} | {data['trades']:2} trades | WR: {wr:5.1f}% | P/L: ${data['pnl']:+7.2f}")
    
    # Analysis by Mistake
    print("\n⚠️  Mistakes Analysis:")
    print("-" * 60)
    mistakes = {}
    for t in trades:
        m = t.get("mistake", "None")
        if m not in mistakes:
            mistakes[m] = {"count": 0, "pnl": 0}
        mistakes[m]["count"] += 1
        mistakes[m]["pnl"] += t.get("pnl", 0)
    
    for m, data in sorted(mistakes.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"   {m:15} | {data['count']:2} times | P/L: ${data['pnl']:+7.2f}")
    
    # Recent Trades
    print("\n📝 Recent Trades (Last 5):")
    print("-" * 60)
    for t in reversed(trades[-5:]):
        status = "✅" if t.get("pnl", 0) > 0 else "❌" if t.get("pnl", 0) < 0 else "⚪"
        coin_qty = t.get('coin_quantity', t.get('position_size', 0) / t.get('entry_price', 1))
        print(f"\n  {status} {t.get('pair', '?')} {t.get('side', '?')}")
        print(f"     Qty: {coin_qty:.2f} | Entry: {t.get('entry_price', '?')} → Exit: {t.get('exit_price', '?')}")
        print(f"     Pattern: {t.get('entry_pattern', '?')} ({t.get('confluence_count', 0)} confluences)")
        print(f"     Session: {t.get('session', '?')} | Emotion: {t.get('emotion_before', '?')}")
        print(f"     P/L: ${t.get('pnl', 0):.2f} | R:R: {t.get('rr_ratio', '?')}")
        if t.get('lesson', 'None') != 'None':
            print(f"     💡 Lesson: {t.get('lesson')}")
    
    print("\n" + "="*60)

def clear_all_trades():
    """ลบ trades ทั้งหมด"""
    print("\n" + "="*60)
    print("   ⚠️  CLEAR ALL TRADES")
    print("="*60)
    
    trades = load_trades()
    if not trades:
        print("\n📭 No trades to clear.")
        return
    
    print(f"\n📊 Current trades: {len(trades)}")
    print(f"💰 Total P/L: ${sum(t.get('pnl', 0) for t in trades):.2f}")
    print("\n⚠️  WARNING: This action cannot be undone!")
    
    confirm = input("\nType 'YES' to confirm: ").strip()
    if confirm == "YES":
        save_trades([])
        print("\n✅ All trades cleared!")
    else:
        print("\n❌ Cancelled.")

def delete_specific_trade():
    """ลบ trade เฉพาะรายการ"""
    trades = load_trades()
    if not trades:
        print("\n📭 No trades to delete.")
        return
    
    print("\n📝 Select trade to delete:")
    print("-" * 60)
    for i, t in enumerate(reversed(trades), 1):
        status = "✅" if t.get("pnl", 0) > 0 else "❌"
        print(f"{i}. {status} {t.get('pair', '?')} {t.get('side', '?')} - "
              f"{t.get('entry_pattern', '?')} - P/L: ${t.get('pnl', 0):.2f}")
    print(f"{len(trades) + 1}. Cancel")
    
    while True:
        try:
            choice = int(input(f"\nSelect (1-{len(trades) + 1}): "))
            if choice == len(trades) + 1:
                return
            if 1 <= choice <= len(trades):
                deleted = trades.pop(len(trades) - choice)
                save_trades(trades)
                print(f"✅ Deleted: {deleted.get('pair')}")
                return
        except ValueError:
            print("❌ Please enter a number")

def export_to_csv():
    """Export trades เป็น CSV"""
    trades = load_trades()
    if not trades:
        print("\n📭 No trades to export.")
        return
    
    filename = f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    fieldnames = [
        "pair", "side", "entry_price", "exit_price", "entry_time", "exit_time",
        "duration", "pnl", "pnl_percentage", "coin_quantity", "position_size",
        "entry_pattern", "entry_timeframe", "confluence_count", "confluence_list",
        "has_sweep", "session", "trend", "volatility", "htf_bias", "news_event",
        "leverage", "risk_percent", "sl_price", "tp_price", "rr_ratio",
        "exit_reason", "exit_pattern", "exit_timeframe", "partial_close",
        "emotion_before", "emotion_during", "emotion_after", "followed_plan",
        "mistake", "lesson", "screenshot", "notes", "timestamp"
    ]
    
    for t in trades:
        if isinstance(t.get("confluence_list"), list):
            t["confluence_list"] = " | ".join(t["confluence_list"])
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(trades)
    
    print(f"\n✅ Exported to: {filename}")

def trade_logger_menu():
    """เมนูหลัก"""
    while True:
        print("\n" + "="*60)
        print("   📊 TRADE LOGGER PRO")
        print("="*60)
        print("\n1. Log new trade (Auto Calculate)")
        print("2. Show statistics (Advanced)")
        print("3. Export to CSV")
        print("4. Clear all trades")
        print("5. Delete specific trade")
        print("0. Back to main menu")
        
        choice = input("\nSelect (0-5): ").strip()
        
        if choice == "1":
            log_trade()
        elif choice == "2":
            show_statistics()
        elif choice == "3":
            export_to_csv()
        elif choice == "4":
            clear_all_trades()
        elif choice == "5":
            delete_specific_trade()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    trade_logger_menu()