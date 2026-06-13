import os

print("\n" + "=" * 60)
print("   ADD NEW COIN TO WATCHLIST")
print("=" * 60)

# อ่าน coins เดิม
try:
    with open('coins.txt', 'r') as f:
        existing = [line.strip() for line in f if line.strip()]
except:
    existing = []

print(f"\nCurrent coins ({len(existing)}):")
for coin in existing:
    print(f"  - {coin}")

# เพิ่มเหรียญใหม่
print("\n" + "-" * 60)
new_coin = input("Enter new coin (e.g., PEPEUSDT): ").strip().upper()

# เพิ่ม .P ถ้ายังไม่มี
if not new_coin.endswith('.P'):
    new_coin += '.P'

# เช็คซ้ำ
if new_coin in existing:
    print(f"\n⚠️  {new_coin} already in list! (Duplicate)")
else:
    with open('coins.txt', 'a') as f:
        f.write(f"\n{new_coin}")
    print(f"\n✅ Added {new_coin} to watchlist!")
    print(f"Total coins: {len(existing) + 1}")

print()