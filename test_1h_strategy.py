#!/usr/bin/env python3
"""
Test 1H Strategy with High Win Rate and 1:3 RR
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest import Backtester
from strategies import TradingStrategies
from config import TradingConfig

def test_1h_strategies():
    """Test optimized 1H strategies"""
    
    print("🔥 TEST 1H STRATEGIES - HIGH WIN RATE")
    print("=" * 60)
    
    # Tính toán thời gian test
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 tháng để test
    
    print(f"📅 Từ: {start_date.strftime('%Y-%m-%d')}")
    print(f"📅 Đến: {end_date.strftime('%Y-%m-%d')}")
    print(f"💰 Số tiền ban đầu: 10,000 USDT")
    print("=" * 60)
    
    # Tạo backtester
    backtester = Backtester()
    
    # Test các chiến lược 1H
    strategies = [
        ('ema_rsi', 'EMA + RSI (1H)'),
        ('bollinger_stochastic', 'Bollinger + Stochastic (1H)'),
        ('high_winrate', 'High Win Rate Strategy (1H)')
    ]
    
    results = []
    
    for strategy_code, strategy_name in strategies:
        print(f"\n📊 Testing {strategy_name}...")
        
        try:
            result = backtester.run_backtest(
                symbol='BTCUSDT',
                start_date=start_date,
                end_date=end_date,
                initial_balance=10000,
                strategy_name=strategy_code
            )
            
            if result:
                metrics = result['metrics']
                results.append({
                    'strategy': strategy_name,
                    'return': result['total_return'],
                    'final_balance': result['final_balance'],
                    'total_trades': metrics['total_trades'],
                    'winning_trades': metrics['winning_trades'],
                    'losing_trades': metrics['losing_trades'],
                    'win_rate': metrics['win_rate'],
                    'profit_factor': metrics['profit_factor'],
                    'max_drawdown': metrics['max_drawdown'],
                    'sharpe_ratio': metrics['sharpe_ratio']
                })
                
                print(f"   ✅ Hoàn thành!")
                print(f"   💰 Lợi nhuận: {result['total_return']:+.2f}%")
                print(f"   📈 Tổng lệnh: {metrics['total_trades']}")
                print(f"   🎯 Tỷ lệ thắng: {metrics['win_rate']:.1f}%")
                print(f"   📊 Profit Factor: {metrics['profit_factor']:.2f}")
                print(f"   📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
                
                # Kiểm tra mục tiêu
                if metrics['win_rate'] >= 60:
                    print(f"   🎯 ĐẠT MỤC TIÊU: Win rate >= 60%")
                else:
                    print(f"   ⚠️ CHƯA ĐẠT: Win rate < 60%")
                    
            else:
                print(f"   ❌ Không có kết quả")
                
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
    
    # In kết quả tổng hợp
    if results:
        print("\n" + "=" * 80)
        print("📊 KẾT QUẢ TỔNG HỢP")
        print("=" * 80)
        
        # Sắp xếp theo win rate
        results.sort(key=lambda x: x['win_rate'], reverse=True)
        
        print(f"{'Chiến lược':<30} {'Lợi nhuận':<10} {'Lệnh':<6} {'Thắng%':<8} {'PF':<6} {'DD%':<6}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['strategy']:<30} {result['return']:>+8.2f}% {result['total_trades']:>6} {result['win_rate']:>6.1f}% {result['profit_factor']:>5.2f} {result['max_drawdown']:>5.2f}%")
        
        # Chiến lược tốt nhất theo win rate
        best_winrate = results[0]
        print(f"\n🏆 CHIẾN LƯỢC TỐT NHẤT (Win Rate): {best_winrate['strategy']}")
        print(f"   🎯 Tỷ lệ thắng: {best_winrate['win_rate']:.1f}%")
        print(f"   💰 Lợi nhuận: {best_winrate['return']:+.2f}%")
        print(f"   📈 Tổng lệnh: {best_winrate['total_trades']}")
        
        # Chiến lược tốt nhất theo lợi nhuận
        best_profit = max(results, key=lambda x: x['return'])
        print(f"\n💰 CHIẾN LƯỢC TỐT NHẤT (Lợi nhuận): {best_profit['strategy']}")
        print(f"   💰 Lợi nhuận: {best_profit['return']:+.2f}%")
        print(f"   🎯 Tỷ lệ thắng: {best_profit['win_rate']:.1f}%")
        
        # Thống kê tổng thể
        print(f"\n📊 THỐNG KÊ TỔNG THỂ:")
        avg_winrate = np.mean([r['win_rate'] for r in results])
        avg_return = np.mean([r['return'] for r in results])
        high_winrate_count = len([r for r in results if r['win_rate'] >= 60])
        
        print(f"   🎯 Tỷ lệ thắng trung bình: {avg_winrate:.1f}%")
        print(f"   💰 Lợi nhuận trung bình: {avg_return:+.2f}%")
        print(f"   ✅ Chiến lược đạt >= 60% win rate: {high_winrate_count}/{len(results)}")
        
        # Đánh giá hiệu quả
        print(f"\n📈 ĐÁNH GIÁ HIỆU QUẢ:")
        if avg_winrate >= 60:
            print(f"   ✅ ĐẠT MỤC TIÊU: Tỷ lệ thắng trung bình >= 60%")
        else:
            print(f"   ⚠️ CHƯA ĐẠT: Tỷ lệ thắng trung bình < 60%")
        
        if avg_return > 0:
            print(f"   ✅ CÓ LÃI: Lợi nhuận trung bình > 0%")
        else:
            print(f"   ❌ LỖ: Lợi nhuận trung bình < 0%")
        
        # Lưu kết quả
        save_choice = input(f"\n💾 Có muốn lưu kết quả ra file Excel không? (y/n): ").lower()
        if save_choice == 'y':
            filename = f"1h_strategy_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            df = pd.DataFrame(results)
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
            
            print(f"💾 Kết quả đã lưu vào: {filename}")
        
        print("=" * 80)
        
    else:
        print("❌ Không có kết quả nào!")

def test_single_strategy():
    """Test một chiến lược cụ thể"""
    
    print("🎯 TEST CHIẾN LƯỢC ĐƠN LẺ")
    print("=" * 50)
    
    print("Chọn chiến lược:")
    print("1. EMA + RSI (1H)")
    print("2. Bollinger + Stochastic (1H)")
    print("3. High Win Rate Strategy (1H)")
    
    choice = input("\nChọn (1-3): ")
    
    strategy_map = {
        '1': 'ema_rsi',
        '2': 'bollinger_stochastic', 
        '3': 'high_winrate'
    }
    
    if choice not in strategy_map:
        print("❌ Lựa chọn không hợp lệ!")
        return
    
    strategy_code = strategy_map[choice]
    
    # Test với 1 tháng dữ liệu
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\n📊 Testing {strategy_code}...")
    print(f"📅 Từ: {start_date.strftime('%Y-%m-%d')}")
    print(f"📅 Đến: {end_date.strftime('%Y-%m-%d')}")
    
    backtester = Backtester()
    
    try:
        result = backtester.run_backtest(
            symbol='BTCUSDT',
            start_date=start_date,
            end_date=end_date,
            initial_balance=10000,
            strategy_name=strategy_code
        )
        
        if result:
            metrics = result['metrics']
            print(f"\n✅ KẾT QUẢ:")
            print(f"   💰 Lợi nhuận: {result['total_return']:+.2f}%")
            print(f"   📈 Tổng lệnh: {metrics['total_trades']}")
            print(f"   🎯 Tỷ lệ thắng: {metrics['win_rate']:.1f}%")
            print(f"   📊 Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"   📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
            
            if metrics['win_rate'] >= 60:
                print(f"   🎯 ĐẠT MỤC TIÊU: Win rate >= 60%")
            else:
                print(f"   ⚠️ CHƯA ĐẠT: Win rate < 60%")
        else:
            print("❌ Không có kết quả")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def main():
    """Main function"""
    print("🔥 1H STRATEGY TESTER")
    print("=" * 50)
    
    while True:
        print("\nChọn loại test:")
        print("1. Test tất cả chiến lược 1H")
        print("2. Test chiến lược đơn lẻ")
        print("3. Thoát")
        
        choice = input("\nChọn (1-3): ")
        
        if choice == '1':
            test_1h_strategies()
        elif choice == '2':
            test_single_strategy()
        elif choice == '3':
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
