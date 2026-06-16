#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Tools - Main Menu
Binance Futures Trading Assistant
"""

import os
import sys

def print_menu():
    """แสดงเมนูหลัก"""
    print("\n" + "="*50)
    print("   TRADING TOOLS - BINANCE FUTURES")
    print("="*50)
    print("\n1. Custom Ranking (Choose Sort)")
    print("2. Quick Scan (By Score)")
    print("3. Check Watchlist")
    print("4. Check Single Coin")
    print("5. Add New Coin")
    print("6. Remove Coin")
    print("7. Scan and Ask AI")
    print("8. Open OpenCode")
    print("9. Start Web App (Mobile)")
    print("10. Trade Logger")
    print("11. Remove Duplicates")
    print("12. Exit")
    print("\n" + "="*50)

def custom_ranking():
    """Custom Ranking Menu"""
    try:
        from custom_rank import custom_ranking_menu
        custom_ranking_menu()
    except ImportError:
        print("\n❌ Error: custom_rank.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def quick_scan():
    """Quick Scan by Score"""
    try:
        from quick_check import quick_scan
        quick_scan()
    except ImportError:
        print("\n❌ Error: quick_check.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def check_watchlist():
    """Check Watchlist"""
    try:
        from check_watchlist import check_watchlist
        check_watchlist()
    except ImportError:
        print("\n❌ Error: check_watchlist.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def check_single_coin():
    """Check Single Coin"""
    try:
        from quick_check import check_single_coin
        check_single_coin()  # ✅ เรียกแค่ครั้งเดียว
    except ImportError:
        print("\n❌ Error: quick_check.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def add_new_coin():
    """Add New Coin"""
    try:
        from add_coin import add_coin
        add_coin()
    except ImportError:
        print("\n❌ Error: add_coin.py not found!")
    except Exception as e:
        print(f"\n Error: {e}")

def remove_coin():
    """Remove Coin"""
    try:
        from remove_coin import remove_coin
        remove_coin()
    except ImportError:
        print("\n❌ Error: remove_coin.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def scan_and_ask_ai():
    """Scan and Ask AI"""
    try:
        from scan_and_ask import scan_and_ask
        scan_and_ask()
    except ImportError:
        print("\n Error: scan_and_ask.py not found!")
    except Exception as e:
        print(f"\n Error: {e}")

def open_opencode():
    """Open OpenCode in VS Code"""
    print("\n🚀 Opening OpenCode...")
    try:
        os.system("code --command opencode.startSession")
    except Exception as e:
        print(f"❌ Error opening OpenCode: {e}")
        print("   Make sure VS Code and OpenCode extension are installed.")

def start_web_app():
    """Start Web App for Mobile"""
    print("\n📱 Starting Web App...")
    try:
        os.system("python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def trade_logger():
    """Trade Logger - บันทึกและวิเคราะห์การเทรด"""
    try:
        from trade_logger import trade_logger_menu
        trade_logger_menu()
    except ImportError:
        print("\n❌ Error: trade_logger.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def remove_duplicates():
    """Remove Duplicate Coins"""
    try:
        from remove_duplicates import remove_duplicates
        remove_duplicates()
    except ImportError:
        print("\n❌ Error: remove_duplicates.py not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def exit_program():
    """ออกจากโปรแกรม"""
    print("\n" + "="*50)
    print("   👋 Thank you for using Trading Tools!")
    print("   Goodbye and happy trading!")
    print("="*50 + "\n")
    sys.exit(0)

def main_menu():
    """เมนูหลัก"""
    while True:
        try:
            print_menu()
            choice = input("Select (1-12): ").strip()
            
            if choice == "1":
                custom_ranking()
            elif choice == "2":
                quick_scan()
            elif choice == "3":
                check_watchlist()
            elif choice == "4":
                check_single_coin()  # ✅ เรียกครั้งเดียว
            elif choice == "5":
                add_new_coin()
            elif choice == "6":
                remove_coin()
            elif choice == "7":
                scan_and_ask_ai()
            elif choice == "8":
                open_opencode()
            elif choice == "9":
                start_web_app()
            elif choice == "10":
                trade_logger()
            elif choice == "11":
                remove_duplicates()
            elif choice == "12":
                exit_program()
            else:
                print("\n❌ Invalid choice. Please select 1-12.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main_menu()