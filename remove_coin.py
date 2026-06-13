import os

print("\n" + "=" * 60)
print("   REMOVE COIN FROM WATCHLIST")
print("=" * 60)

# อ่าน coins.txt
try:
    with open('coins.txt', 'r') as f:
        coins = [line.strip() for line in f if line.strip()]
    
    print(f"\nCurrent coins ({len(coins)}):")
    for i, coin in enumerate(coins, 1):
        print(f"  {i:2}. {coin}")
    
    print("\n" + "-" * 60)
    print("Enter coin name to remove (e.g., XLMUSDT): ", end="")
    coin_to_remove = input().strip().upper()
    
    # เพิ่ม .P ถ้ายังไม่มี
    if not coin_to_remove.endswith('.P'):
        coin_to_remove += '.P'
    
    if coin_to_remove in coins:
        coins.remove(coin_to_remove)
        
        # บันทึกใหม่
        with open('coins.txt', 'w') as f:
            for coin in coins:
                f.write(f"{coin}\n")
        
        print(f"\n✅ Removed {coin_to_remove} successfully!")
        print(f"Remaining coins: {len(coins)}")
    else:
        print(f"\n❌ {coin_to_remove} not found in watchlist!")
        
except FileNotFoundError:
    print("\n❌ coins.txt not found!")

print()