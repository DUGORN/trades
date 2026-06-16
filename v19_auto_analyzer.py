#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SESSION REVERSAL MODE V19 - Auto Analyzer (Fixed v2)
แก้ไข: clean_symbol() ทำงานถูกต้อง
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time
import re

# ==========================================
# CONFIGURATION
# ==========================================
BINANCE_API = "https://fapi.binance.com/fapi/v1"
TRADING_PAIR = "BRETTUSDT"
LEVERAGE = 75
RISK_PERCENT = 25
MAX_DISTANCE_CRYPTO = 1.5
MAX_DISTANCE_GOLD = 2.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 10

# ==========================================
# SYMBOL CLEANER (แก้ไขแล้ว)
# ==========================================
def clean_symbol(symbol):
    """ล้าง symbol ให้ถูกต้อง"""
    if not symbol:
        return ""
    
    # ลบ whitespace
    symbol = symbol.strip()
    
    # ลบตัวอักษรที่ไม่ใช่ ASCII (เช่น สระภาษาไทย)
    symbol = re.sub(r'[^\x00-\x7F]+', '', symbol)
    
    # แปลงเป็นตัวพิมพ์ใหญ่
    symbol = symbol.upper()
    
    # ลบ .P หรือ P ที่ท้ายสุด (เช่น BRETTUSDT.P → BRETTUSDT)
    if symbol.endswith('.P'):
        symbol = symbol[:-2]
    elif symbol.endswith('P') and not symbol.endswith('USDT'):
        symbol = symbol[:-1]
    
    # ลบอักขระพิเศษที่เหลือ
    symbol = re.sub(r'[^A-Za-z0-9]', '', symbol)
    
    # ถ้าไม่มี USDT ต่อท้าย ให้เติม
    if not symbol.endswith('USDT'):
        symbol = symbol + 'USDT'
    
    return symbol

# ==========================================
# BINANCE DATA FETCHER
# ==========================================
def api_request(url, params=None):
    """เรียก API พร้อม retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"   ⚠️  Connection error, retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(2)
            else:
                print(f"   ❌ Connection failed after {MAX_RETRIES} attempts")
                print(f"   💡 Check your internet connection")
                return None
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"   ⚠️  Timeout, retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(2)
            else:
                print(f"   ❌ Request timeout")
                return None
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    return None

def get_klines(symbol, interval, limit=100):
    """ดึงข้อมูลแท่งเทียน"""
    url = f"{BINANCE_API}/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    return api_request(url, params)

def get_ticker(symbol):
    """ดึงข้อมูลราคาปัจจุบัน"""
    url = f"{BINANCE_API}/ticker/24hr"
    params = {"symbol": symbol}
    data = api_request(url, params)
    
    if not data:
        return None
    
    try:
        return {
            "price": float(data["lastPrice"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "volume": float(data["volume"]),
            "change_percent": float(data["priceChangePercent"])
        }
    except (KeyError, ValueError) as e:
        print(f"   ❌ Error parsing ticker data: {e}")
        return None

def get_daily_levels(symbol):
    """คำนวณ PDH/PDL"""
    klines = get_klines(symbol, "1d", limit=2)
    if not klines or len(klines) < 2:
        return None
    
    prev_day = klines[0]
    return {
        "pdh": float(prev_day[2]),
        "pdl": float(prev_day[3]),
        "open": float(prev_day[1]),
        "close": float(prev_day[4])
    }

# ==========================================
# V19 ANALYSIS ENGINE
# ==========================================
def calculate_distance(current, level):
    """คำนวณระยะห่าง %"""
    if level == 0:
        return 0
    return ((current - level) / level) * 100

def analyze_multi_timeframe(symbol):
    """วิเคราะห์หลาย Timeframe"""
    print("\n📊 Analyzing Multi-Timeframe...")
    
    timeframes = {"4H": "4h", "1H": "1h", "15m": "15m", "1m": "1m"}
    analysis = {}
    
    for tf_name, tf_interval in timeframes.items():
        print(f"   Checking {tf_name}...")
        klines = get_klines(symbol, tf_interval, limit=50)
        if not klines or len(klines) < 10:
            print(f"   ⚠️  Not enough data for {tf_name}")
            continue
        
        closes = [float(k[4]) for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        
        # EMA 200
        if len(closes) >= 200:
            ema_200 = sum(closes[-200:]) / 200
        else:
            ema_200 = sum(closes) / len(closes)
        
        # MACD
        ema_12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else closes[-1]
        ema_26 = sum(closes[-26:]) / 26 if len(closes) >= 26 else closes[-1]
        macd_line = ema_12 - ema_26
        
        current_price = closes[-1]
        
        analysis[tf_name] = {
            "price": current_price,
            "ema_200": ema_200,
            "above_ema": current_price > ema_200,
            "macd_bullish": macd_line > 0,
            "trend": "BULL" if current_price > ema_200 else "BEAR",
            "high": max(highs[-24:]) if len(highs) >= 24 else max(highs),
            "low": min(lows[-24:]) if len(lows) >= 24 else min(lows)
        }
    
    return analysis

def check_v19_conditions(symbol, analysis, daily_levels):
    """ตรวจสอบเงื่อนไข V19"""
    print("\n🎯 Checking V19 Conditions...")
    
    if not daily_levels or not analysis:
        return None
    
    current_price = analysis.get("1m", {}).get("price", 0)
    if current_price == 0:
        current_price = analysis.get("15m", {}).get("price", 0)
    
    pdh = daily_levels["pdh"]
    pdl = daily_levels["pdl"]
    
    dist_pdh = calculate_distance(current_price, pdh)
    dist_pdl = calculate_distance(current_price, pdl)
    
    tf_4h = analysis.get("4H", {})
    tf_1h = analysis.get("1H", {})
    
    # LONG Conditions
    long_conditions = {
        "4H_near_pdl": calculate_distance(tf_4h.get("price", 0), pdl) < 2,
        "4H_waterfall_cold": not tf_4h.get("above_ema", False),
        "1H_holding_structure": tf_1h.get("above_ema", False),
        "15m_in_zone": dist_pdl < 1.5,
        "1m_sweep_low": dist_pdl < 0.5 and dist_pdl > -0.5,
        "distance_ok": abs(dist_pdl) <= MAX_DISTANCE_CRYPTO
    }
    
    # SHORT Conditions
    short_conditions = {
        "4H_near_pdh": calculate_distance(tf_4h.get("price", 0), pdh) < 2,
        "4H_waterfall_hot": tf_4h.get("above_ema", False),
        "1H_weak_structure": not tf_1h.get("above_ema", False),
        "15m_in_zone": dist_pdh < 1.5,
        "1m_sweep_high": dist_pdh < 0.5 and dist_pdh > -0.5,
        "distance_ok": abs(dist_pdh) <= MAX_DISTANCE_CRYPTO
    }
    
    long_score = sum(long_conditions.values())
    short_score = sum(short_conditions.values())
    
    return {
        "long": {
            "score": long_score,
            "conditions": long_conditions,
            "ready": long_score >= 4 and long_conditions["distance_ok"]
        },
        "short": {
            "score": short_score,
            "conditions": short_conditions,
            "ready": short_score >= 4 and short_conditions["distance_ok"]
        },
        "current_price": current_price,
        "pdh": pdh,
        "pdl": pdl,
        "dist_pdh": dist_pdh,
        "dist_pdl": dist_pdl
    }

def calculate_entry_exit(signal_type, analysis, daily_levels):
    """คำนวณ Entry/SL/TP"""
    pdh = daily_levels["pdh"]
    pdl = daily_levels["pdl"]
    
    if signal_type == "LONG":
        sweep = pdl * 0.998
        re_entry = pdl * 1.002
        sl = pdl * 0.995
        tp1 = pdh * 0.998
        tp2 = pdh * 1.005
    else:
        sweep = pdh * 1.002
        re_entry = pdh * 0.998
        sl = pdh * 1.005
        tp1 = pdl * 1.002
        tp2 = pdl * 0.995
    
    return {
        "sweep": round(sweep, 6),
        "re_entry": round(re_entry, 6),
        "sl": round(sl, 6),
        "tp1": round(tp1, 6),
        "tp2": round(tp2, 6)
    }

# ==========================================
# OPENCODE INTEGRATION
# ==========================================
def send_to_opencode(symbol, analysis, v19_result, levels):
    """ส่งข้อมูลไป OpenCode"""
    print("\n🤖 Sending to OpenCode...")
    
    prompt = f"""Analyze {symbol} - SESSION REVERSAL MODE V19

Current Price: {v19_result['current_price']}
PDH: {v19_result['pdh']}
PDL: {v19_result['pdl']}
Distance to PDH: {v19_result['dist_pdh']:+.2f}%
Distance to PDL: {v19_result['dist_pdl']:+.2f}%

Multi-TF Analysis:
4H: {analysis.get('4H', {}).get('trend', 'N/A')}
1H: {analysis.get('1H', {}).get('trend', 'N/A')}

V19 Scores:
LONG: {v19_result['long']['score']}/6
SHORT: {v19_result['short']['score']}/6

Provide: Trade direction, Entry, SL/TP, Confluences needed"""
    
    with open("opencode_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    
    print("✅ Prompt saved to opencode_prompt.txt")
    return prompt

# ==========================================
# DISPLAY RESULTS
# ==========================================
def display_v19_analysis(symbol, v19_result, levels, entry_exit):
    """แสดงผลการวิเคราะห์"""
    print("\n" + "="*60)
    print(f"   SESSION REVERSAL MODE V19 - {symbol}")
    print("="*60)
    
    print(f"\n💰 Current Price: {v19_result['current_price']}")
    print(f"📊 PDH: {v19_result['pdh']} ({v19_result['dist_pdh']:+.2f}%)")
    print(f"📊 PDL: {v19_result['pdl']} ({v19_result['dist_pdl']:+.2f}%)")
    
    print("\n🎯 V19 CONDITIONS:")
    print(f"  LONG Score:  {v19_result['long']['score']}/6 {'✅ READY' if v19_result['long']['ready'] else '⏳ WAITING'}")
    print(f"  SHORT Score: {v19_result['short']['score']}/6 {'✅ READY' if v19_result['short']['ready'] else '⏳ WAITING'}")
    
    if v19_result['long']['ready']:
        print("\n" + "="*60)
        print(f"   {symbol} | LONG")
        print("="*60)
        print(f"\n🔹 SWEEP LOW: {entry_exit['sweep']}")
        print(f"🔹 RE-ENTRY: {entry_exit['re_entry']}")
        print(f"🔹 STOP LOSS: {entry_exit['sl']}")
        print(f"🔹 TP1: {entry_exit['tp1']}")
        print(f"🔹 TP2: {entry_exit['tp2']}")
    elif v19_result['short']['ready']:
        print("\n" + "="*60)
        print(f"   {symbol} | SHORT")
        print("="*60)
        print(f"\n🔹 SWEEP HIGH: {entry_exit['sweep']}")
        print(f"🔹 RE-ENTRY: {entry_exit['re_entry']}")
        print(f"🔹 STOP LOSS: {entry_exit['sl']}")
        print(f"🔹 TP1: {entry_exit['tp1']}")
        print(f"🔹 TP2: {entry_exit['tp2']}")
    else:
        print("\n" + "="*60)
        print(f"   {symbol} | WAIT")
        print("="*60)
        print(f"\n⏳ Waiting for setup")
    
    print("\n" + "="*60)

# ==========================================
# AUTO MONITOR
# ==========================================
def auto_monitor(symbol, interval=60):
    """Auto monitor"""
    print(f"\n🤖 Auto Monitor Started - {symbol}")
    print(f"⏱️  Checking every {interval} seconds...")
    print("Press Ctrl+C to stop\n")
    
    last_signal = None
    
    try:
        while True:
            ticker = get_ticker(symbol)
            if not ticker:
                time.sleep(interval)
                continue
            
            daily_levels = get_daily_levels(symbol)
            analysis = analyze_multi_timeframe(symbol)
            v19_result = check_v19_conditions(symbol, analysis, daily_levels)
            
            if not v19_result:
                time.sleep(interval)
                continue
            
            current_signal = "LONG" if v19_result['long']['ready'] else "SHORT" if v19_result['short']['ready'] else "WAIT"
            
            if current_signal != last_signal and current_signal != "WAIT":
                entry_exit = calculate_entry_exit(current_signal, analysis, daily_levels)
                display_v19_analysis(symbol, v19_result, daily_levels, entry_exit)
                send_to_opencode(symbol, analysis, v19_result, daily_levels)
                last_signal = current_signal
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n👋 Auto monitor stopped")

# ==========================================
# MAIN MENU
# ==========================================
def main():
    """เมนูหลัก"""
    print("\n" + "="*60)
    print("   SESSION REVERSAL MODE V19 - AUTO ANALYZER")
    print("="*60)
    
    # รับ symbol และล้างอัตโนมัติ
    raw_symbol = input(f"\nEnter symbol (default: {TRADING_PAIR}): ").strip()
    if not raw_symbol:
        symbol = TRADING_PAIR
    else:
        symbol = clean_symbol(raw_symbol)
    
    print(f"\n✅ Symbol: {symbol}")
    print(f"   (Cleaned from: '{raw_symbol}')")
    
    # ทดสอบการเชื่อมต่อ
    print("\n🔌 Testing connection to Binance...")
    test = get_ticker(symbol)
    if not test:
        print("\n❌ Cannot connect to Binance API")
        print("💡 Please check:")
        print("   1. Internet connection")
        print("   2. Firewall settings")
        print("   3. Try pinging fapi.binance.com")
        input("\nPress Enter to continue anyway...")
    else:
        print(f"✅ Connected! Current price: {test['price']}")
    
    while True:
        print("\n" + "="*60)
        print("   📊 MAIN MENU")
        print("="*60)
        print("\n1. One-Time Analysis")
        print("2. Auto Monitor (Real-time)")
        print("3. Send to OpenCode")
        print("4. Change Symbol")
        print("5. Test Connection")
        print("0. Exit")
        
        choice = input("\nSelect (0-5): ").strip()
        
        if choice == "1":
            print(f"\n📊 Analyzing {symbol}...")
            
            ticker = get_ticker(symbol)
            daily_levels = get_daily_levels(symbol)
            
            if not ticker or not daily_levels:
                print("\n❌ Failed to fetch data")
                print("💡 Check internet connection or symbol name")
            else:
                analysis = analyze_multi_timeframe(symbol)
                v19_result = check_v19_conditions(symbol, analysis, daily_levels)
                
                if v19_result:
                    entry_exit = calculate_entry_exit(
                        "LONG" if v19_result['long']['ready'] else "SHORT" if v19_result['short']['ready'] else "WAIT",
                        analysis, daily_levels
                    )
                    display_v19_analysis(symbol, v19_result, daily_levels, entry_exit)
                    
                    result = {
                        "symbol": symbol,
                        "timestamp": datetime.now().isoformat(),
                        "current_price": v19_result['current_price'],
                        "pdh": v19_result['pdh'],
                        "pdl": v19_result['pdl'],
                        "long_score": v19_result['long']['score'],
                        "short_score": v19_result['short']['score'],
                        "signal": "LONG" if v19_result['long']['ready'] else "SHORT" if v19_result['short']['ready'] else "WAIT"
                    }
                    
                    with open("v19_analysis.json", "w") as f:
                        json.dump(result, f, indent=2)
                    
                    print("\n✅ Analysis saved to v19_analysis.json")
        
        elif choice == "2":
            auto_monitor(symbol, interval=60)
        
        elif choice == "3":
            ticker = get_ticker(symbol)
            daily_levels = get_daily_levels(symbol)
            
            if not ticker or not daily_levels:
                print("\n❌ Failed to fetch data")
            else:
                analysis = analyze_multi_timeframe(symbol)
                v19_result = check_v19_conditions(symbol, analysis, daily_levels)
                
                if v19_result:
                    prompt = send_to_opencode(symbol, analysis, v19_result, daily_levels)
                    print("\n" + "="*60)
                    print(prompt)
                    print("="*60)
        
        elif choice == "4":
            raw_new = input("\nEnter new symbol: ").strip()
            if raw_new:
                symbol = clean_symbol(raw_new)
                print(f"✅ Changed to: {symbol}")
            else:
                print("❌ Invalid symbol")
        
        elif choice == "5":
            print(f"\n🔌 Testing connection for {symbol}...")
            test = get_ticker(symbol)
            if test:
                print(f"✅ Connected! Price: {test['price']}")
                print(f"   24h Change: {test['change_percent']:+.2f}%")
            else:
                print("❌ Connection failed")
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")
        
        if choice != "2":
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()