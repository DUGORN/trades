#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Check - ตรวจสอบเหรียญแบบรวดเร็ว
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
import requests
import json
import os
from datetime import datetime

# ==========================================
# BINANCE API SETUP (ไม่ต้องใส่ API Key สำหรับ public data)
# ==========================================
BINANCE_API_URL = "https://fapi.binance.com/fapi/v1"

def format_price(price, symbol=""):
    """
    Format ราคาให้เหมาะสมกับมูลค่าของเหรียญ
    """
    try:
        price = float(price)
        
        # ตรวจสอบราคาและเลือกทศนิยมที่เหมาะสม
        if price < 0.001:
            return f"{price:.8f}"  # 8 ตำแหน่ง สำหรับเหรียญราคาต่ำมาก
        elif price < 0.01:
            return f"{price:.6f}"  # 6 ตำแหน่ง สำหรับเหรียญราคาต่ำ
        elif price < 1:
            return f"{price:.4f}"  # 4 ตำแหน่ง สำหรับเหรียญราคาปานกลาง
        elif price < 10:
            return f"{price:.3f}"  # 3 ตำแหน่ง
        elif price < 100:
            return f"{price:.2f}"  # 2 ตำแหน่ง
        else:
            return f"{price:.2f}"  # 2 ตำแหน่ง
    except:
        return str(price)

def get_ticker_info(symbol):
    """ดึงข้อมูลราคาจาก Binance"""
    try:
        # ลบ .P ออกถ้ามี
        symbol = symbol.upper().replace(".P", "")
        
        url = f"{BINANCE_API_URL}/ticker/24hr"
        params = {"symbol": symbol}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "code" in data:
            print(f"❌ Error: {data.get('msg', 'Unknown error')}")
            return None
        
        return {
            "symbol": data.get("symbol", ""),
            "last_price": float(data.get("lastPrice", 0)),
            "high_24h": float(data.get("highPrice", 0)),
            "low_24h": float(data.get("lowPrice", 0)),
            "volume": float(data.get("volume", 0)),
            "quote_volume": float(data.get("quoteVolume", 0)),
            "price_change": float(data.get("priceChange", 0)),
            "price_change_percent": float(data.get("priceChangePercent", 0)),
        }
    except Exception as e:
        print(f"❌ Error fetching ticker: {e}")
        return None

def get_daily_levels(symbol):
    """ดึงข้อมูล PDH/PDL (Previous Day High/Low)"""
    try:
        symbol = symbol.upper().replace(".P", "")
        
        # ดึงข้อมูล kline ของวันก่อนหน้า
        url = f"{BINANCE_API_URL}/klines"
        params = {
            "symbol": symbol,
            "interval": "1d",
            "limit": 2
        }
        
        response = requests.get(url, params=params)
        klines = response.json()
        
        if len(klines) < 2:
            # ถ้าไม่มีข้อมูลวันก่อนหน้า ใช้ข้อมูลปัจจุบัน
            ticker = get_ticker_info(symbol)
            if ticker:
                return {
                    "pdh": ticker["high_24h"],
                    "pdl": ticker["low_24h"],
                    "current": ticker["last_price"]
                }
            return None
        
        # วันก่อนหน้าคือ kline แรก (index 0)
        # kline structure: [open_time, open, high, low, close, ...]
        prev_day = klines[0]
        
        return {
            "pdh": float(prev_day[2]),  # High
            "pdl": float(prev_day[3]),  # Low
            "current": float(prev_day[4])  # Close
        }
    except Exception as e:
        print(f"❌ Error fetching daily levels: {e}")
        return None

def calculate_distance(current, level):
    """คำนวณระยะห่างจาก level (%)"""
    if level == 0:
        return 0
    return ((current - level) / level) * 100

def check_single_coin():
    """ตรวจสอบเหรียญเดียว"""
    print("\n" + "="*60)
    print("   🔍 CHECK SINGLE COIN")
    print("="*60)
    
    symbol = input("\nEnter coin (e.g., BTCUSDT): ").strip()
    if not symbol:
        print("❌ Symbol is required!")
        return
    
    # ดึงข้อมูล
    print(f"\n📊 Fetching data for {symbol.upper()}...")
    
    ticker = get_ticker_info(symbol)
    if not ticker:
        print("❌ Failed to fetch ticker data")
        print("   Make sure the symbol is correct (e.g., BTCUSDT, ETHUSDT)")
        return
    
    daily = get_daily_levels(symbol)
    
    # แสดงผล
    print("\n" + "="*60)
    print(f"  {ticker['symbol']} - {format_price(ticker['last_price'], ticker['symbol'])}")
    print("="*60)
    
    if daily:
        print(f"  PDH: {format_price(daily['pdh'], ticker['symbol'])}")
        print(f"  PDL: {format_price(daily['pdl'], ticker['symbol'])}")
        print(f"  High (24h): {format_price(ticker['high_24h'], ticker['symbol'])}")
        print(f"  Low (24h): {format_price(ticker['low_24h'], ticker['symbol'])}")
        print("="*60)
        
        # คำนวณระยะห่าง
        dist_pdh = calculate_distance(ticker['last_price'], daily['pdh'])
        dist_pdl = calculate_distance(ticker['last_price'], daily['pdl'])
        
        print()
        if abs(dist_pdh) < 2:
            print(f"  📍 Near PDH ({dist_pdh:+.2f}%) ⚠️")
        elif dist_pdh > 0:
            print(f"  📈 Above PDH ({dist_pdh:+.2f}%)")
        else:
            print(f"  📉 Below PDH ({dist_pdh:+.2f}%)")
        
        if abs(dist_pdl) < 2:
            print(f"  📍 Near PDL ({dist_pdl:+.2f}%) ⚠️")
        elif dist_pdl > 0:
            print(f"  📈 Above PDL ({dist_pdl:+.2f}%)")
        else:
            print(f"  📉 Below PDL ({dist_pdl:+.2f}%)")
    else:
        print(f"  Current Price: {format_price(ticker['last_price'], ticker['symbol'])}")
        print(f"  High (24h): {format_price(ticker['high_24h'], ticker['symbol'])}")
        print(f"  Low (24h): {format_price(ticker['low_24h'], ticker['symbol'])}")
    
    # ข้อมูลเพิ่มเติม
    print()
    print(f"  24h Change: {ticker['price_change']:+.4f} ({ticker['price_change_percent']:+.2f}%)")
    print(f"  Volume: {ticker['volume']:,.0f} {ticker['symbol'].replace('USDT', '')}")
    print(f"  Quote Volume: ${ticker['quote_volume']:,.2f} USDT")
    
    # สร้างข้อความสำหรับ copy ไป OpenCode
    print("\n" + "="*60)
    print("  💡 Copy ข้อมูลนี้ไปถาม OpenCode:")
    print("="*60)
    
    copy_text = f"{ticker['symbol']}\n"
    copy_text += f"ราคา: {format_price(ticker['last_price'], ticker['symbol'])}\n"
    
    if daily:
        copy_text += f"PDH: {format_price(daily['pdh'], ticker['symbol'])} | "
        copy_text += f"PDL: {format_price(daily['pdl'], ticker['symbol'])}\n"
        copy_text += f"High: {format_price(ticker['high_24h'], ticker['symbol'])} | "
        copy_text += f"Low: {format_price(ticker['low_24h'], ticker['symbol'])}"
    else:
        copy_text += f"High: {format_price(ticker['high_24h'], ticker['symbol'])} | "
        copy_text += f"Low: {format_price(ticker['low_24h'], ticker['symbol'])}"
    
    print(copy_text)
    print("="*60)
    
    # Copy to clipboard (Windows)
    try:
        import subprocess
        subprocess.run(["clip"], input=copy_text.encode(), check=True)
        print("\n✅ Copied to clipboard!")
    except:
        print("\n⚠️  Could not copy to clipboard. Please copy manually.")
    
    print("\nPress any key to continue...")
    input()

def quick_scan():
    """Quick scan หลายเหรียญ"""
    print("\n" + "="*60)
    print("   🔍 QUICK SCAN")
    print("="*60)
    
    # โหลดรายการเหรียญจากไฟล์
    coins_file = "coins.txt"
    if not os.path.exists(coins_file):
        print(f"\n❌ File '{coins_file}' not found!")
        print("   Please create the file with coin list (one per line)")
        return
    
    with open(coins_file, 'r', encoding='utf-8') as f:
        coins = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not coins:
        print("\n❌ No coins found in file!")
        return
    
    print(f"\n📊 Scanning {len(coins)} coins...\n")
    
    results = []
    for i, coin in enumerate(coins, 1):
        print(f"[{i}/{len(coins)}] Checking {coin}...")
        
        ticker = get_ticker_info(coin)
        if ticker:
            daily = get_daily_levels(coin)
            
            result = {
                "symbol": ticker['symbol'],
                "price": ticker['last_price'],
                "change_pct": ticker['price_change_percent'],
                "volume": ticker['quote_volume'],
            }
            
            if daily:
                result['pdh'] = daily['pdh']
                result['pdl'] = daily['pdl']
                result['dist_pdh'] = calculate_distance(ticker['last_price'], daily['pdh'])
                result['dist_pdl'] = calculate_distance(ticker['last_price'], daily['pdl'])
            
            results.append(result)
    
    # แสดงผลการสแกน
    print("\n" + "="*60)
    print("   📊 SCAN RESULTS")
    print("="*60)
    print(f"\n{'Symbol':<12} {'Price':<12} {'Change':<10} {'Vol (M)':<10} {'Near':<15}")
    print("-" * 60)
    
    for r in results:
        price_str = format_price(r['price'], r['symbol'])
        change_str = f"{r['change_pct']:+.2f}%"
        vol_str = f"{r['volume']/1000000:.1f}M"
        
        near = ""
        if 'dist_pdh' in r and abs(r['dist_pdh']) < 2:
            near = "PDH"
        elif 'dist_pdl' in r and abs(r['dist_pdl']) < 2:
            near = "PDL"
        
        print(f"{r['symbol']:<12} {price_str:<12} {change_str:<10} {vol_str:<10} {near:<15}")
    
    print("\nPress any key to continue...")
    input()

def custom_ranking_menu():
    """Custom Ranking Menu"""
    print("\n" + "="*60)
    print("   📊 CUSTOM RANKING MENU")
    print("="*60)
    print("\n1. Sort by Score (Default)")
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
    
    choice = input("\nSelect (0-10): ").strip()
    
    if choice == "0":
        return
    elif choice == "1":
        print("\n⚠️  Feature coming soon!")
    elif choice == "2":
        print("\n⚠️  Feature coming soon!")
    else:
        print("\n⚠️  Feature coming soon!")
    
    print("\nPress any key to continue...")
    input()

def quick_check_menu():
    """เมนูหลักของ Quick Check"""
    while True:
        print("\n" + "="*60)
        print("   CUSTOM RANKING MENU")
        print("="*60)
        print("\n1. Sort by Score (Default)")
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
        
        choice = input("\nSelect (0-10): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            print("\n⚠️  Feature coming soon!")
        elif choice == "2":
            print("\n⚠️  Feature coming soon!")
        else:
            print("\n⚠️  Feature coming soon!")
        
        print("\nPress any key to continue...")
        input()

if __name__ == "__main__":
    # สำหรับทดสอบเดี่ยวๆ
    check_single_coin()