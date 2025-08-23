#!/usr/bin/env python3
"""
Quick Backtest Script - Chạy backtest nhanh với cấu hình có sẵn
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest import Backtester

def quick_backtest_examples():
    """Chạy các ví dụ backtest nhanh"""
    
    print("🚀 QUICK BACKTEST EXAMPLES")
    print("=" * 50)
    
    # Tạo backtester
    backtester = Backtester()
    
    # Các cấu hình backtest mẫu
    test_configs = [
        {
            'name': 'Test 1: 1 tháng gần đây - Tất cả chiến lược',
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now(),
            'strategy': 'all',
            'balance': 10000
        },
        {
            'name': 'Test 2: 3 tháng gần đây - EMA + RSI',
            'start_date': datetime.now() - timedelta(days=90),
            'end_date': datetime.now(),
            'strategy': 'ema_rsi',
            'balance': 10000
        },
        {
            'name': 'Test 3: 1 tuần gần đây - Bollinger + Stochastic',
            'start_date': datetime.now() - timedelta(days=7),
            'end_date': datetime.now(),
            'strategy': 'bollinger_stochastic',
            'balance': 10000
        },
        {
            'name': 'Test 4: 6 tháng gần đây - MACD + VWAP',
            'start_date': datetime.now() - timedelta(days=180),
            'end_date': datetime.now(),
            'strategy': 'macd_vwap',
            'balance': 10000
        }
    ]
    
    results_summary = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📊 {config['name']}")
        print("-" * 40)
        
        try:
            results = backtester.run_backtest(
                symbol='BTCUSDT',
                start_date=config['start_date'],
                end_date=config['end_date'],
                initial_balance=config['balance'],
                strategy_name=config['strategy']
            )
            
            if results:
                metrics = results['metrics']
                print(f"✅ Hoàn thành!")
                print(f"   💰 Lợi nhuận: {results['total_return']:+.2f}%")
                print(f"   📈 Tổng lệnh: {metrics['total_trades']}")
                print(f"   🎯 Tỷ lệ thắng: {metrics['win_rate']:.1f}%")
                print(f"   📊 Profit Factor: {metrics['profit_factor']:.2f}")
                
                results_summary.append({
                    'test': config['name'],
                    'return': results['total_return'],
                    'trades': metrics['total_trades'],
                    'win_rate': metrics['win_rate'],
                    'profit_factor': metrics['profit_factor']
                })
            else:
                print("❌ Thất bại!")
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    # In tổng kết
    if results_summary:
        print("\n" + "=" * 50)
        print("📊 TỔNG KẾT CÁC TEST")
        print("=" * 50)
        
        df = pd.DataFrame(results_summary)
        print(df.to_string(index=False))
        
        # Tìm test tốt nhất
        best_test = max(results_summary, key=lambda x: x['return'])
        print(f"\n🏆 Test tốt nhất: {best_test['test']}")
        print(f"   Lợi nhuận: {best_test['return']:+.2f}%")

def backtest_specific_period():
    """Backtest cho một khoảng thời gian cụ thể"""
    
    print("\n🎯 BACKTEST KHOẢNG THỜI GIAN CỤ THỂ")
    print("=" * 50)
    
    # Ví dụ: Backtest tháng 1/2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    print(f"📅 Khoảng thời gian: {start_date.strftime('%Y-%m-%d')} -> {end_date.strftime('%Y-%m-%d')}")
    
    backtester = Backtester()
    
    # Test tất cả chiến lược
    strategies = ['all', 'ema_rsi', 'bollinger_stochastic', 'macd_vwap', 'ichimoku', 'vsa_obv']
    
    strategy_results = []
    
    for strategy in strategies:
        print(f"\n📊 Testing {strategy}...")
        
        try:
            results = backtester.run_backtest(
                symbol='BTCUSDT',
                start_date=start_date,
                end_date=end_date,
                initial_balance=10000,
                strategy_name=strategy
            )
            
            if results:
                metrics = results['metrics']
                strategy_results.append({
                    'strategy': strategy,
                    'return': results['total_return'],
                    'trades': metrics['total_trades'],
                    'win_rate': metrics['win_rate'],
                    'profit_factor': metrics['profit_factor'],
                    'max_drawdown': metrics['max_drawdown']
                })
                print(f"   ✅ {results['total_return']:+.2f}% return")
            else:
                print(f"   ❌ Không có kết quả")
                
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
    
    # In so sánh chiến lược
    if strategy_results:
        print("\n" + "=" * 60)
        print("📊 SO SÁNH CÁC CHIẾN LƯỢC")
        print("=" * 60)
        
        df = pd.DataFrame(strategy_results)
        df = df.sort_values('return', ascending=False)
        print(df.to_string(index=False))
        
        # Chiến lược tốt nhất
        best_strategy = df.iloc[0]
        print(f"\n🏆 Chiến lược tốt nhất: {best_strategy['strategy']}")
        print(f"   Lợi nhuận: {best_strategy['return']:+.2f}%")
        print(f"   Tỷ lệ thắng: {best_strategy['win_rate']:.1f}%")

def main():
    """Main function"""
    print("🔥 BTCUSDT QUICK BACKTEST")
    print("=" * 50)
    
    while True:
        print("\nChọn loại backtest:")
        print("1. Chạy các test mẫu")
        print("2. Backtest tháng 1/2024 (so sánh chiến lược)")
        print("3. Thoát")
        
        choice = input("\nChọn (1-3): ")
        
        if choice == '1':
            quick_backtest_examples()
        elif choice == '2':
            backtest_specific_period()
        elif choice == '3':
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
