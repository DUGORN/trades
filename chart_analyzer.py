#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Analyzer - วาดกราฟและตีเส้น Entry/SL/TP อัตโนมัติ (Fixed v4)
"""

import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
import numpy as np
import os
import re

BINANCE_API = "https://fapi.binance.com/fapi/v1"

def clean_symbol(symbol):
    """ล้าง symbol"""
    if not symbol:
        return ""
    symbol = symbol.strip().upper()
    symbol = re.sub(r'[^\x00-\x7F]+', '', symbol)
    if symbol.endswith('.P'):
        symbol = symbol[:-2]
    elif symbol.endswith('P') and not symbol.endswith('USDT'):
        symbol = symbol[:-1]
    symbol = re.sub(r'[^A-Za-z0-9]', '', symbol)
    if not symbol.endswith('USDT'):
        symbol = symbol + 'USDT'
    return symbol

def get_valid_symbols():
    """ดึงรายการ symbol ที่ถูกต้อง"""
    try:
        url = f"{BINANCE_API}/exchangeInfo"
        response = requests.get(url, timeout=10)
        data = response.json()
        symbols = set()
        for s in data.get('symbols', []):
            if s.get('status') == 'TRADING' and s.get('contractType') == 'PERPETUAL':
                symbols.add(s['symbol'])
        return symbols
    except:
        return set()

def get_klines(symbol, interval, limit=100):
    """ดึงข้อมูลแท่งเทียน"""
    try:
        symbol = clean_symbol(symbol)
        
        print(f"\n   Symbol: {symbol}")
        print(f"   Interval: {interval}")
        
        valid_symbols = get_valid_symbols()
        if valid_symbols and symbol not in valid_symbols:
            print(f"   ❌ Symbol '{symbol}' not found in Binance Futures!")
            if valid_symbols:
                similar = [s for s in valid_symbols if symbol.replace('USDT','') in s]
                if similar:
                    print(f"   💡 Suggestions: {', '.join(list(similar)[:5])}")
            return None
        
        url = f"{BINANCE_API}/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "code" in data:
            print(f"   ❌ Binance API Error: {data.get('msg', 'Unknown error')}")
            return None
        
        if not isinstance(data, list) or len(data) == 0:
            print(f"   ❌ No data found")
            return None
        
        times = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for k in data:
            times.append(datetime.fromtimestamp(int(k[0]) / 1000))
            opens.append(float(k[1]))
            highs.append(float(k[2]))
            lows.append(float(k[3]))
            closes.append(float(k[4]))
            volumes.append(float(k[5]))
        
        print(f"   ✅ Fetched {len(times)} candles")
        
        return {
            "times": times,
            "opens": opens,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "volumes": volumes
        }
    except Exception as e:
        print(f"   ❌ Error fetching klines: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_ema(data, period):
    """คำนวณ EMA"""
    if len(data) < period:
        return [None] * len(data)
    
    ema = []
    multiplier = 2 / (period + 1)
    sma = sum(data[:period]) / period
    ema.append(sma)
    
    for i in range(period, len(data)):
        value = (data[i] - ema[-1]) * multiplier + ema[-1]
        ema.append(value)
    
    return [None] * (period - 1) + ema

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """คำนวณ MACD"""
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    
    macd_line = []
    for i in range(len(closes)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line.append(ema_fast[i] - ema_slow[i])
        else:
            macd_line.append(0)  # เปลี่ยนจาก None เป็น 0
    
    macd_values = [m for m in macd_line if m is not None]
    if len(macd_values) >= signal:
        signal_line = calculate_ema(macd_values, signal)
        none_count = len(macd_line) - len(macd_values)
        signal_line = [0] * none_count + signal_line  # เปลี่ยนจาก None เป็น 0
    else:
        signal_line = [0] * len(macd_line)
    
    histogram = []
    for i in range(len(macd_line)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(0)  # เปลี่ยนจาก None เป็น 0
    
    return macd_line, signal_line, histogram

def draw_candlestick(ax, times, opens, highs, lows, closes, width=0.6):
    """วาดกราฟ Candlestick"""
    for i in range(len(times)):
        open_price = opens[i]
        close_price = closes[i]
        high_price = highs[i]
        low_price = lows[i]
        
        color = 'green' if close_price >= open_price else 'red'
        
        ax.plot([times[i], times[i]], [low_price, high_price], color=color, linewidth=0.5)
        
        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)
        
        rect = Rectangle((times[i] - timedelta(minutes=width*10), body_bottom), 
                         timedelta(minutes=width*20), body_height,
                         facecolor=color, edgecolor=color, linewidth=0.5)
        ax.add_patch(rect)

def draw_levels(ax, levels, current_price, last_time, colors=None, labels=None):
    """ตีเส้น Levels"""
    if colors is None:
        colors = ['blue', 'red', 'green', 'lime']
    if labels is None:
        labels = ['Entry', 'Stop Loss', 'TP1', 'TP2']
    
    for level, color, label in zip(levels, colors, labels):
        if level and level > 0:
            ax.axhline(y=level, color=color, linewidth=1.5, linestyle='--', alpha=0.7, label=label)
            ax.text(last_time + timedelta(minutes=5), level, f'{label}: {level:.6f}', 
                   color=color, fontsize=8, verticalalignment='bottom')

def create_chart(symbol, interval='15m', limit=100, levels=None, save_path=None):
    """สร้างกราฟทั้งหมด"""
    print(f"\n📊 Creating chart for {symbol} ({interval})...")
    
    data = get_klines(symbol, interval, limit)
    if not data:
        print("❌ Failed to fetch data")
        return None
    
    times = data["times"]
    opens = data["opens"]
    highs = data["highs"]
    lows = data["lows"]
    closes = data["closes"]
    volumes = data["volumes"]
    
    ema_20 = calculate_ema(closes, 20)
    ema_50 = calculate_ema(closes, 50)
    ema_200 = calculate_ema(closes, 200)
    macd_line, signal_line, histogram = calculate_macd(closes)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 10), height_ratios=[3, 1, 1])
    fig.suptitle(f'{symbol} - {interval} Chart', fontsize=14, fontweight='bold')
    
    draw_candlestick(ax1, times, opens, highs, lows, closes)
    
    if any(v is not None for v in ema_20):
        ax1.plot(times, ema_20, label='EMA 20', color='orange', linewidth=1)
    if any(v is not None for v in ema_50):
        ax1.plot(times, ema_50, label='EMA 50', color='purple', linewidth=1)
    if any(v is not None for v in ema_200):
        ax1.plot(times, ema_200, label='EMA 200', color='blue', linewidth=1)
    
    if levels:
        colors = ['blue', 'red', 'green', 'lime']
        labels = ['Entry', 'Stop Loss', 'TP1', 'TP2']
        draw_levels(ax1, levels, closes[-1], times[-1], colors, labels)
    
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    colors = ['green' if closes[i] >= opens[i] else 'red' for i in range(len(closes))]
    ax2.bar(times, volumes, color=colors, alpha=0.5, width=0.8)
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)
    
    ax3.plot(times, macd_line, label='MACD', color='blue', linewidth=1)
    ax3.plot(times, signal_line, label='Signal', color='red', linewidth=1)
    
    # แก้ histogram: แทนที่ None ด้วย 0
    histogram_clean = [h if h is not None else 0 for h in histogram]
    hist_colors = ['green' if h >= 0 else 'red' for h in histogram_clean]
    ax3.bar(times, histogram_clean, color=hist_colors, alpha=0.3, width=0.8)
    ax3.axhline(y=0, color='black', linewidth=0.5)
    ax3.set_ylabel('MACD')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    for ax in [ax1, ax2, ax3]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Chart saved to: {save_path}")
    else:
        plt.show()
    
    plt.close()
    return save_path

def analyze_and_chart(symbol, interval='15m', entry=None, sl=None, tp1=None, tp2=None):
    """วิเคราะห์และสร้างกราฟ"""
    print(f"\n🎯 Analyzing {symbol}...")
    
    levels = []
    if entry:
        levels.append(float(entry))
    if sl:
        levels.append(float(sl))
    if tp1:
        levels.append(float(tp1))
    if tp2:
        levels.append(float(tp2))
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = f"chart_{symbol.replace('.P','')}_{interval}_{timestamp}.png"
    
    result = create_chart(symbol, interval, 100, levels if levels else None, save_path)
    
    return result

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   CHART ANALYZER - Create Trading Chart")
    print("="*60)
    
    # รับ Symbol
    while True:
        symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip()
        if symbol:
            symbol = clean_symbol(symbol)
            break
        print("❌ Symbol is required!")
    
    # รับ Interval
    while True:
        interval = input("Enter interval (1m/5m/15m/30m/1h/4h/1d): ").strip().lower()
        if not interval:
            interval = "15m"
            break
        
        interval_map = {
            "1": "1m", "1m": "1m",
            "3": "3m", "3m": "3m",
            "5": "5m", "5m": "5m",
            "15": "15m", "15m": "15m",
            "30": "30m", "30m": "30m",
            "1h": "1h", "60": "1h",
            "4h": "4h", "240": "4h",
            "1d": "1d", "d": "1d"
        }
        
        if interval in interval_map:
            interval = interval_map[interval]
            break
        print("❌ Invalid interval! Try again.")
    
    print(f"\n✅ Symbol: {symbol}")
    print(f"✅ Interval: {interval}")
    
    # รับ Trade Levels
    print("\n" + "-"*60)
    print("Enter trade levels (or press Enter to skip):")
    print("-"*60)
    
    entry = None
    sl = None
    tp1 = None
    tp2 = None
    
    try:
        entry_input = input("Entry Price: ").strip()
        if entry_input:
            entry = float(entry_input)
        
        sl_input = input("Stop Loss: ").strip()
        if sl_input:
            sl = float(sl_input)
        
        tp1_input = input("TP1: ").strip()
        if tp1_input:
            tp1 = float(tp1_input)
        
        tp2_input = input("TP2: ").strip()
        if tp2_input:
            tp2 = float(tp2_input)
        
    except ValueError as e:
        print(f"\n⚠️  Invalid number format: {e}")
        print("   Continuing without levels...")
    
    # สร้างกราฟ
    print("\n" + "="*60)
    analyze_and_chart(symbol, interval, entry, sl, tp1, tp2)
    print("="*60)