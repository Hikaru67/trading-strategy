#!/usr/bin/env python3
"""
Quick 1 year backtest - Test individual strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest import Backtester

def quick_1year_test():
    """Quick test of individual strategies on 1 year data"""
    
    print("🔥 QUICK BACKTEST 1 NĂM")
    print("=" * 50)
    
    # Tính toán thời gian 1 năm trước
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print(f"📅 Từ: {start_date.strftime('%Y-%m-%d')}")
    print(f"📅 Đến: {end_date.strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    # Tạo backtester
    backtester = Backtester()
    
    # Test từng chiến lược riêng lẻ
    strategies = [
        ('ema_rsi', 'EMA + RSI'),
        ('bollinger_stochastic', 'Bollinger + Stochastic'),
        ('macd_vwap', 'MACD + VWAP'),
        ('ichimoku', 'Ichimoku'),
        ('vsa_obv', 'VSA + OBV')
    ]
    
    results = []
    
    for strategy_code, strategy_name in strategies:
        print(f"\n📊 {strategy_name}...")
        
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
    
    # In tổng kết
    if results:
        print("\n" + "=" * 50)
        print("📊 TỔNG KẾT")
        print("=" * 50)
        
        # Sắp xếp theo lợi nhuận
        results.sort(key=lambda x: x['return'], reverse=True)
        
        print(f"{'Chiến lược':<20} {'Lợi nhuận':<10} {'Lệnh':<6} {'Thắng%':<8}")
        print("-" * 50)
        
        for result in results:
            print(f"{result['strategy']:<20} {result['return']:>+8.2f}% {result['trades']:>6} {result['win_rate']:>6.1f}%")
        
        # Chiến lược tốt nhất
        best = results[0]
        print(f"\n🏆 TỐT NHẤT: {best['strategy']} ({best['return']:+.2f}%)")
        
        # Chiến lược tệ nhất
        worst = results[-1]
        print(f"💥 TỆ NHẤT: {worst['strategy']} ({worst['return']:+.2f}%)")
        
        # Thống kê
        avg_return = np.mean([r['return'] for r in results])
        profitable_count = len([r for r in results if r['return'] > 0])
        print(f"\n📊 Trung bình: {avg_return:+.2f}% | Có lãi: {profitable_count}/{len(results)}")

if __name__ == "__main__":
    quick_1year_test()
