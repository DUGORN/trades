with open('coins.txt', 'r') as f:
    coins = [line.strip() for line in f if line.strip()]

original_count = len(coins)
unique_coins = list(dict.fromkeys(coins))
new_count = len(unique_coins)

with open('coins.txt', 'w') as f:
    for coin in unique_coins:
        f.write(f"{coin}\n")

print(f"\nOriginal: {original_count} coins")
print(f"After remove duplicates: {new_count} coins")
print(f"Removed: {original_count - new_count} duplicates")
print()