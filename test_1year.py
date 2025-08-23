#!/usr/bin/env python3
"""
Test all strategies on 1 year of historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest import Backtester

def test_1year_backtest():
    """Test all strategies on 1 year of data"""
    
    print("🔥 BACKTEST 1 NĂM GẦN ĐÂY")
    print("=" * 60)
    
    # Tính toán thời gian 1 năm trước
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print(f"📅 Từ: {start_date.strftime('%Y-%m-%d')}")
    print(f"📅 Đến: {end_date.strftime('%Y-%m-%d')}")
    print(f"💰 Số tiền ban đầu: 10,000 USDT")
    print("=" * 60)
    
    # Tạo backtester
    backtester = Backtester()
    
    # Danh sách chiến lược để test
    strategies = [
        ('all', 'Tất cả chiến lược'),
        ('ema_rsi', 'EMA + RSI'),
        ('bollinger_stochastic', 'Bollinger + Stochastic'),
        ('macd_vwap', 'MACD + VWAP'),
        ('ichimoku', 'Ichimoku'),
        ('vsa_obv', 'VSA + OBV')
    ]
    
    results = []
    
    for strategy_code, strategy_name in strategies:
        print(f"\n📊 Testing {strategy_name}...")
        
        try:
            # Chạy backtest
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
                    'code': strategy_code,
                    'return': result['total_return'],
                    'final_balance': result['final_balance'],
                    'total_trades': metrics['total_trades'],
                    'winning_trades': metrics['winning_trades'],
                    'losing_trades': metrics['losing_trades'],
                    'win_rate': metrics['win_rate'],
                    'profit_factor': metrics['profit_factor'],
                    'max_drawdown': metrics['max_drawdown'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'total_pnl': metrics['total_pnl'],
                    'average_pnl': metrics['average_pnl']
                })
                
                print(f"   ✅ Hoàn thành!")
                print(f"   💰 Lợi nhuận: {result['total_return']:+.2f}%")
                print(f"   📈 Tổng lệnh: {metrics['total_trades']}")
                print(f"   🎯 Tỷ lệ thắng: {metrics['win_rate']:.1f}%")
                print(f"   📊 Profit Factor: {metrics['profit_factor']:.2f}")
                print(f"   📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
            else:
                print(f"   ❌ Không có kết quả")
                
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
    
    # In kết quả tổng hợp
    if results:
        print("\n" + "=" * 80)
        print("📊 KẾT QUẢ BACKTEST 1 NĂM")
        print("=" * 80)
        
        # Sắp xếp theo lợi nhuận
        results.sort(key=lambda x: x['return'], reverse=True)
        
        # Tạo DataFrame để hiển thị đẹp hơn
        df = pd.DataFrame(results)
        
        # Hiển thị bảng tổng quan
        print("\n📈 BẢNG TỔNG QUAN:")
        print("-" * 80)
        print(f"{'Chiến lược':<20} {'Lợi nhuận':<10} {'Lệnh':<6} {'Thắng%':<8} {'PF':<6} {'DD%':<6}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['strategy']:<20} {result['return']:>+8.2f}% {result['total_trades']:>6} {result['win_rate']:>6.1f}% {result['profit_factor']:>5.2f} {result['max_drawdown']:>5.2f}%")
        
        # Chiến lược tốt nhất
        best = results[0]
        print(f"\n🏆 CHIẾN LƯỢC TỐT NHẤT: {best['strategy']}")
        print(f"   💰 Lợi nhuận: {best['return']:+.2f}%")
        print(f"   💵 Số tiền cuối: {best['final_balance']:,.2f} USDT")
        print(f"   📈 Tổng lệnh: {best['total_trades']}")
        print(f"   🎯 Tỷ lệ thắng: {best['win_rate']:.1f}%")
        print(f"   📊 Profit Factor: {best['profit_factor']:.2f}")
        print(f"   📉 Max Drawdown: {best['max_drawdown']:.2f}%")
        print(f"   📊 Sharpe Ratio: {best['sharpe_ratio']:.2f}")
        
        # Chiến lược tệ nhất
        worst = results[-1]
        print(f"\n💥 CHIẾN LƯỢC TỆ NHẤT: {worst['strategy']}")
        print(f"   💰 Lợi nhuận: {worst['return']:+.2f}%")
        print(f"   📈 Tổng lệnh: {worst['total_trades']}")
        print(f"   🎯 Tỷ lệ thắng: {worst['win_rate']:.1f}%")
        
        # Thống kê tổng thể
        print(f"\n📊 THỐNG KÊ TỔNG THỂ:")
        print(f"   📈 Tổng số lệnh: {sum(r['total_trades'] for r in results)}")
        print(f"   💰 Lợi nhuận trung bình: {np.mean([r['return'] for r in results]):+.2f}%")
        print(f"   🎯 Tỷ lệ thắng trung bình: {np.mean([r['win_rate'] for r in results]):.1f}%")
        print(f"   📊 Profit Factor trung bình: {np.mean([r['profit_factor'] for r in results]):.2f}")
        
        # Phân tích risk
        print(f"\n⚠️ PHÂN TÍCH RISK:")
        profitable_strategies = [r for r in results if r['return'] > 0]
        if profitable_strategies:
            print(f"   ✅ Chiến lược có lãi: {len(profitable_strategies)}/{len(results)}")
            print(f"   💰 Lợi nhuận trung bình (có lãi): {np.mean([r['return'] for r in profitable_strategies]):+.2f}%")
        else:
            print(f"   ❌ Không có chiến lược nào có lãi")
        
        # Lưu kết quả
        save_choice = input(f"\n💾 Có muốn lưu kết quả ra file Excel không? (y/n): ").lower()
        if save_choice == 'y':
            filename = f"backtest_1year_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Sheet tổng quan
                summary_df = df[['strategy', 'return', 'final_balance', 'total_trades', 'win_rate', 'profit_factor', 'max_drawdown', 'sharpe_ratio']]
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Sheet chi tiết
                detail_df = df[['strategy', 'return', 'total_pnl', 'average_pnl', 'winning_trades', 'losing_trades', 'win_rate', 'profit_factor', 'max_drawdown', 'sharpe_ratio']]
                detail_df.to_excel(writer, sheet_name='Details', index=False)
            
            print(f"💾 Kết quả đã lưu vào: {filename}")
        
        print("=" * 80)
        
    else:
        print("❌ Không có kết quả nào!")

if __name__ == "__main__":
    test_1year_backtest()
