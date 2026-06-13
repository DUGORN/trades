import os
import sys

def menu():
    while True:
        os.system('cls')
        print("=" * 60)
        print("   TRADING TOOLS - BINANCE FUTURES")
        print("=" * 60)
        print()
        print("1. สแกนหา setup ทั้งหมด")
        print("2. เช็ค watchlist")
        print("3. เช็คเหรียญเดียว")
        print("4. เพิ่มเหรียญใหม่")
        print("5. เปิด OpenCode")
        print("6. ออก")
        print()
        print("=" * 60)
        
        choice = input("เลือก (1-6): ").strip()
        
        if choice == '1':
            os.system('cls')
            os.system('python find_setups.py')
            input("\nPress Enter to continue...")
        elif choice == '2':
            os.system('cls')
            os.system('python check_watchlist.py')
            input("\nPress Enter to continue...")
        elif choice == '3':
            os.system('cls')
            coin = input("Coin (เช่น BTCUSDT): ").strip()
            os.system(f'python quick_check.py {coin}')
            input("\nPress Enter to continue...")
        elif choice == '4':
            os.system('cls')
            os.system('python add_coin.py')
            input("\nPress Enter to continue...")
        elif choice == '5':
            os.system('start opencode')
        elif choice == '6':
            print("\nGoodbye!\n")
            sys.exit(0)

if __name__ == "__main__":
    menu()