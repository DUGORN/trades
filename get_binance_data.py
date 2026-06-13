import requests
import json
from datetime import datetime

def get_binance_futures_data(symbol, interval='15m', limit=100):
    """ดึงข้อมูลจาก Binance Futures API"""
    
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {
        'symbol': symbol.upper(),
        'interval': interval,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # แปลงข้อมูล
        latest = data[-1]
        prev = data[-2]
        
        current_price = float(latest[4])  # Close price
        high = float(latest[2])
        low = float(latest[3])
        open_price = float(latest[1])
        volume = float(latest[5])
        
        # คำนวณ PDH, PDL (จากแท่งก่อนหน้า)
        pdh = float(prev[2])  # Previous High
        pdl = float(prev[3])  # Previous Low
        
        print(f"\n{symbol} | {datetime.now().strftime('%H:%M:%S')}")
        print(f"ราคาปัจจุบัน: {current_price}")
        print(f"High: {high} | Low: {low}")
        print(f"PDH: {pdh} | PDL: {pdl}")
        print(f"Volume: {volume:,.0f}")
        
        # ตรวจสอบระยะห่างจาก PDH/PDL
        dist_from_pdh = ((current_price - pdh) / pdh) * 100
        dist_from_pdl = ((pdl - current_price) / pdl) * 100
        
        print(f"ระยะจาก PDH: {dist_from_pdh:+.2f}%")
        print(f"ระยะจาก PDL: {dist_from_pdl:+.2f}%")
        
        # ตรวจสอบว่าเป็น Near PDH/PDL ไหม (ภายใน 1.5%)
        near_pdh = dist_from_pdh <= 1.5 and dist_from_pdh >= -1.5
        near_pdl = dist_from_pdl <= 1.5 and dist_from_pdl >= -1.5
        
        print(f"Near PDH: {near_pdh}")
        print(f"Near PDL: {near_pdl}")
        
        return {
            'symbol': symbol,
            'price': current_price,
            'high': high,
            'low': low,
            'pdh': pdh,
            'pdl': pdl,
            'near_pdh': near_pdh,
            'near_pdl': near_pdl
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# ทดสอบ
if __name__ == "__main__":
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
    
    for symbol in symbols:
        get_binance_futures_data(symbol)
        print("-" * 50)