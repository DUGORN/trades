import requests

print("📊 แสดงเหรียญตามระดับ Leverage\n")

url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
response = requests.get(url)
data = response.json()

tiers = {
    '125x': [],
    '100x': [],
    '75x': [],
    '50x': [],
    '25x': [],
    'Below 25x': []
}

for symbol in data['symbols']:
    if symbol['quoteAsset'] == 'USDT' and symbol['status'] == 'TRADING':
        max_leverage = int(symbol.get('maxLeverage', 0))
        coin_name = symbol['symbol'] + '.P'
        
        if max_leverage >= 125:
            tiers['125x'].append(coin_name)
        elif max_leverage >= 100:
            tiers['100x'].append(coin_name)
        elif max_leverage >= 75:
            tiers['75x'].append(coin_name)
        elif max_leverage >= 50:
            tiers['50x'].append(coin_name)
        elif max_leverage >= 25:
            tiers['25x'].append(coin_name)
        else:
            tiers['Below 25x'].append(coin_name)

print("=" * 70)
for tier, coins in tiers.items():
    if coins:
        print(f"\n🔸 {tier}: {len(coins)} เหรียญ")
        print("-" * 70)
        for coin in sorted(coins)[:10]:
            print(f"  {coin}")
        if len(coins) > 10:
            print(f"  ... และอีก {len(coins) - 10} เหรียญ")

print("\n" + "=" * 70)