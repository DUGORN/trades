from flask import Flask, render_template
import requests

app = Flask(__name__)

def scan_coins():
    with open('coins.txt', 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]

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
                    'price': f"{current:,.4f}" if current < 1 else f"{current:,.2f}",
                    'score': round(score, 1),
                    'direction': direction,
                    'distance': f"{min(dist_pdh, dist_pdl):.2f}",
                    'volume': f"{volume:,.0f}"
                })
        except:
            pass
            
    setups.sort(key=lambda x: x['score'], reverse=True)
    return setups[:15] # เอาแค่ Top 15

@app.route('/')
def index():
    setups = scan_coins()
    return render_template('index.html', setups=setups)

if __name__ == '__main__':
    print("\n" + "="*50)
    print(" Web App พร้อมใช้งาน!")
    print("เปิดมือถือ เข้าเว็บ: http://192.168.1.xxx:5000")
    print("(ดู IP เครื่องคอมจากคำสั่ง ipconfig)")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)