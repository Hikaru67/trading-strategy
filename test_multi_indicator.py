#!/usr/bin/env python3
"""
Test Multi-Indicator Strategy - Combines all indicators for high accuracy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest import Backtester
from strategies import TradingStrategies
from config import TradingConfig

def test_multi_indicator():
    """Test the multi-indicator strategy"""
    
    print("🔥 MULTI-INDICATOR STRATEGY TEST")
    print("=" * 60)
    print("🎯 Target: 60%+ win rate with 1:3 RR")
    print("📊 Combines: EMA, RSI, Bollinger Bands, MACD, VWAP, Stochastic, OBV")
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
    
    print("\n📊 Testing Multi-Indicator Strategy...")
    
    try:
        result = backtester.run_backtest(
            symbol='BTCUSDT',
            start_date=start_date,
            end_date=end_date,
            initial_balance=10000,
            strategy_name='multi_indicator'
        )
        
        if result:
            metrics = result['metrics']
            trades = result['trades']
            
            print(f"✅ Hoàn thành!")
            print(f"   💰 Lợi nhuận: {result['total_return']:+.2f}%")
            print(f"   💵 Số tiền cuối: {result['final_balance']:,.2f} USDT")
            print(f"   📈 Tổng lệnh: {metrics['total_trades']}")
            print(f"   ✅ Lệnh thắng: {metrics['winning_trades']}")
            print(f"   ❌ Lệnh thua: {metrics['losing_trades']}")
            print(f"   🎯 Tỷ lệ thắng: {metrics['win_rate']:.1f}%")
            print(f"   📊 Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"   📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
            print(f"   📊 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            
            # Kiểm tra mục tiêu
            print(f"\n🎯 ĐÁNH GIÁ MỤC TIÊU:")
            if metrics['win_rate'] >= 60:
                print(f"   ✅ ĐẠT MỤC TIÊU: Win rate >= 60% ({metrics['win_rate']:.1f}%)")
            else:
                print(f"   ⚠️ CHƯA ĐẠT: Win rate < 60% ({metrics['win_rate']:.1f}%)")
            
            if metrics['profit_factor'] > 1:
                print(f"   ✅ CÓ LÃI: Profit Factor > 1 ({metrics['profit_factor']:.2f})")
            else:
                print(f"   ❌ LỖ: Profit Factor < 1 ({metrics['profit_factor']:.2f})")
            
            if result['total_return'] > 0:
                print(f"   ✅ CÓ LÃI: Tổng lợi nhuận > 0% ({result['total_return']:+.2f}%)")
            else:
                print(f"   ❌ LỖ: Tổng lợi nhuận < 0% ({result['total_return']:+.2f}%)")
            
            # Phân tích chi tiết
            if trades:
                print(f"\n📋 PHÂN TÍCH CHI TIẾT:")
                
                # Lệnh thắng lớn nhất
                winning_trades = [t for t in trades if t['pnl'] > 0]
                if winning_trades:
                    best_trade = max(winning_trades, key=lambda x: x['pnl'])
                    print(f"   🏆 Lệnh thắng lớn nhất: {best_trade['pnl']:+,.2f} USDT")
                    print(f"      Chiến lược: {best_trade['strategy']}")
                    print(f"      Thời gian: {best_trade['entry_time']} -> {best_trade['exit_time']}")
                
                # Lệnh thua lớn nhất
                losing_trades = [t for t in trades if t['pnl'] < 0]
                if losing_trades:
                    worst_trade = min(losing_trades, key=lambda x: x['pnl'])
                    print(f"   💥 Lệnh thua lớn nhất: {worst_trade['pnl']:+,.2f} USDT")
                    print(f"      Chiến lược: {worst_trade['strategy']}")
                    print(f"      Thời gian: {worst_trade['entry_time']} -> {worst_trade['exit_time']}")
                
                # Thống kê theo tháng
                print(f"\n📅 THỐNG KÊ THEO THÁNG:")
                monthly_stats = {}
                for trade in trades:
                    month = trade['entry_time'].strftime('%Y-%m')
                    if month not in monthly_stats:
                        monthly_stats[month] = {'trades': 0, 'wins': 0, 'pnl': 0}
                    
                    monthly_stats[month]['trades'] += 1
                    monthly_stats[month]['pnl'] += trade['pnl']
                    if trade['pnl'] > 0:
                        monthly_stats[month]['wins'] += 1
                
                for month, stats in sorted(monthly_stats.items()):
                    win_rate = (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0
                    print(f"   {month}: {stats['trades']} lệnh, {stats['wins']} thắng ({win_rate:.1f}%), {stats['pnl']:+,.2f} USDT")
            
            # Lưu kết quả
            save_choice = input(f"\n💾 Có muốn lưu kết quả ra file Excel không? (y/n): ").lower()
            if save_choice == 'y':
                filename = f"multi_indicator_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Summary sheet
                    summary_data = {
                        'Metric': ['Total Return (%)', 'Final Balance', 'Total Trades', 'Winning Trades', 
                                 'Losing Trades', 'Win Rate (%)', 'Profit Factor', 'Max Drawdown (%)', 'Sharpe Ratio'],
                        'Value': [result['total_return'], result['final_balance'], metrics['total_trades'],
                                metrics['winning_trades'], metrics['losing_trades'], metrics['win_rate'],
                                metrics['profit_factor'], metrics['max_drawdown'], metrics['sharpe_ratio']]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Trades sheet
                    if trades:
                        trades_df = pd.DataFrame(trades)
                        trades_df.to_excel(writer, sheet_name='Trades', index=False)
                
                print(f"💾 Kết quả đã lưu vào: {filename}")
            
        else:
            print("❌ Không có kết quả")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    print("=" * 60)

def test_strategy_comparison():
    """So sánh multi-indicator với các chiến lược khác"""
    
    print("\n🔄 SO SÁNH CHIẾN LƯỢC")
    print("=" * 60)
    
    # Tính toán thời gian test
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # 2 tháng để test nhanh
    
    print(f"📅 Từ: {start_date.strftime('%Y-%m-%d')}")
    print(f"📅 Đến: {end_date.strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    # Tạo backtester
    backtester = Backtester()
    
    # Test các chiến lược
    strategies = [
        ('multi_indicator', 'Multi-Indicator'),
        ('ema_rsi', 'EMA + RSI'),
        ('bollinger_stochastic', 'Bollinger + Stochastic'),
        ('macd_vwap', 'MACD + VWAP')
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
                    'trades': metrics['total_trades'],
                    'win_rate': metrics['win_rate'],
                    'profit_factor': metrics['profit_factor'],
                    'max_drawdown': metrics['max_drawdown']
                })
                
                print(f"   💰 {result['total_return']:+.2f}% | 📈 {metrics['total_trades']} lệnh | 🎯 {metrics['win_rate']:.1f}% | 📊 PF: {metrics['profit_factor']:.2f}")
            else:
                print(f"   ❌ Không có kết quả")
                
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
    
    # In so sánh
    if results:
        print("\n" + "=" * 60)
        print("📊 SO SÁNH KẾT QUẢ")
        print("=" * 60)
        
        # Sắp xếp theo win rate
        results.sort(key=lambda x: x['win_rate'], reverse=True)
        
        print(f"{'Chiến lược':<20} {'Lợi nhuận':<10} {'Lệnh':<6} {'Thắng%':<8} {'PF':<6}")
        print("-" * 60)
        
        for result in results:
            print(f"{result['strategy']:<20} {result['return']:>+8.2f}% {result['trades']:>6} {result['win_rate']:>6.1f}% {result['profit_factor']:>5.2f}")
        
        # Chiến lược tốt nhất
        best = results[0]
        print(f"\n🏆 CHIẾN LƯỢC TỐT NHẤT: {best['strategy']}")
        print(f"   🎯 Tỷ lệ thắng: {best['win_rate']:.1f}%")
        print(f"   💰 Lợi nhuận: {best['return']:+.2f}%")
        
        print("=" * 60)

def main():
    """Main function"""
    print("🔥 MULTI-INDICATOR STRATEGY TESTER")
    print("=" * 50)
    
    while True:
        print("\nChọn loại test:")
        print("1. Test Multi-Indicator Strategy")
        print("2. So sánh với các chiến lược khác")
        print("3. Thoát")
        
        choice = input("\nChọn (1-3): ")
        
        if choice == '1':
            test_multi_indicator()
        elif choice == '2':
            test_strategy_comparison()
        elif choice == '3':
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
