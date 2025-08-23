#!/usr/bin/env python3
"""
Interactive Backtest Script for BTCUSDT Trading Strategy
Chạy backtest với dữ liệu nến quá khứ từ Binance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import sys
from backtest import Backtester
from config import TradingConfig

def print_banner():
    """In banner chào mừng"""
    print("=" * 70)
    print("🔥 BTCUSDT TRADING STRATEGY BACKTESTER")
    print("=" * 70)
    print("Chạy backtest với dữ liệu nến quá khứ từ Binance")
    print("=" * 70)

def get_user_input():
    """Lấy input từ user"""
    print("\n📊 CẤU HÌNH BACKTEST")
    print("-" * 40)
    
    # Chọn thời gian backtest
    print("\n1. Chọn khoảng thời gian backtest:")
    print("   a) 1 tuần gần đây")
    print("   b) 1 tháng gần đây") 
    print("   c) 3 tháng gần đây")
    print("   d) 6 tháng gần đây")
    print("   e) 1 năm gần đây")
    print("   f) Tùy chỉnh")
    
    time_choice = input("\nChọn (a-f): ").lower()
    
    if time_choice == 'a':
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    elif time_choice == 'b':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif time_choice == 'c':
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
    elif time_choice == 'd':
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now()
    elif time_choice == 'e':
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
    elif time_choice == 'f':
        print("\nNhập ngày bắt đầu (YYYY-MM-DD):")
        start_str = input("Ví dụ 2024-01-01: ")
        print("Nhập ngày kết thúc (YYYY-MM-DD):")
        end_str = input("Ví dụ 2024-01-31: ")
        
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
        except ValueError:
            print("❌ Định dạng ngày không đúng! Sử dụng YYYY-MM-DD")
            return None
    else:
        print("❌ Lựa chọn không hợp lệ!")
        return None
    
    # Chọn chiến lược
    print("\n2. Chọn chiến lược:")
    print("   a) Tất cả chiến lược (best signal)")
    print("   b) EMA + RSI")
    print("   c) Bollinger Bands + Stochastic")
    print("   d) MACD + VWAP")
    print("   e) Ichimoku")
    print("   f) VSA + OBV")
    
    strategy_choice = input("\nChọn (a-f): ").lower()
    
    strategy_map = {
        'a': 'all',
        'b': 'ema_rsi',
        'c': 'bollinger_stochastic',
        'd': 'macd_vwap',
        'e': 'ichimoku',
        'f': 'vsa_obv'
    }
    
    if strategy_choice not in strategy_map:
        print("❌ Lựa chọn không hợp lệ!")
        return None
    
    strategy_name = strategy_map[strategy_choice]
    
    # Số tiền ban đầu
    print("\n3. Số tiền ban đầu (USDT):")
    try:
        initial_balance = float(input("Nhập số tiền (mặc định 10000): ") or "10000")
    except ValueError:
        print("❌ Số tiền không hợp lệ! Sử dụng 10000")
        initial_balance = 10000
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'strategy_name': strategy_name,
        'initial_balance': initial_balance
    }

def run_backtest_with_progress(config):
    """Chạy backtest với progress bar"""
    print(f"\n🚀 BẮT ĐẦU BACKTEST")
    print(f"📅 Từ: {config['start_date'].strftime('%Y-%m-%d')}")
    print(f"📅 Đến: {config['end_date'].strftime('%Y-%m-%d')}")
    print(f"💰 Số tiền ban đầu: {config['initial_balance']:,.0f} USDT")
    print(f"📊 Chiến lược: {config['strategy_name']}")
    print("-" * 50)
    
    # Tạo backtester
    backtester = Backtester()
    
    # Chạy backtest
    print("⏳ Đang tải dữ liệu lịch sử...")
    results = backtester.run_backtest(
        symbol='BTCUSDT',
        start_date=config['start_date'],
        end_date=config['end_date'],
        initial_balance=config['initial_balance'],
        strategy_name=config['strategy_name']
    )
    
    if results:
        print("✅ Backtest hoàn thành!")
        return results
    else:
        print("❌ Backtest thất bại!")
        return None

def print_detailed_results(results):
    """In kết quả chi tiết"""
    if not results:
        return
    
    metrics = results['metrics']
    trades = results['trades']
    
    print("\n" + "=" * 70)
    print("📈 KẾT QUẢ BACKTEST")
    print("=" * 70)
    
    # Thống kê cơ bản
    print(f"💰 Số tiền cuối: {results['final_balance']:,.2f} USDT")
    print(f"📊 Tổng lợi nhuận: {results['total_return']:+.2f}%")
    print(f"📈 Tổng số lệnh: {metrics['total_trades']}")
    print(f"✅ Lệnh thắng: {metrics['winning_trades']}")
    print(f"❌ Lệnh thua: {metrics['losing_trades']}")
    print(f"🎯 Tỷ lệ thắng: {metrics['win_rate']:.2f}%")
    
    # Thống kê nâng cao
    print(f"\n📊 THỐNG KÊ NÂNG CAO:")
    print(f"💰 Tổng PnL: {metrics['total_pnl']:+,.2f} USDT")
    print(f"📊 PnL trung bình: {metrics['average_pnl']:+,.2f} USDT")
    print(f"📈 Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"📊 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    # Phân tích lệnh
    if trades:
        print(f"\n📋 PHÂN TÍCH LỆNH:")
        
        # Lệnh thắng lớn nhất
        winning_trades = [t for t in trades if t['pnl'] > 0]
        if winning_trades:
            best_trade = max(winning_trades, key=lambda x: x['pnl'])
            print(f"🏆 Lệnh thắng lớn nhất: {best_trade['pnl']:+,.2f} USDT")
            print(f"   Chiến lược: {best_trade['strategy']}")
            print(f"   Thời gian: {best_trade['entry_time']} -> {best_trade['exit_time']}")
        
        # Lệnh thua lớn nhất
        losing_trades = [t for t in trades if t['pnl'] < 0]
        if losing_trades:
            worst_trade = min(losing_trades, key=lambda x: x['pnl'])
            print(f"💥 Lệnh thua lớn nhất: {worst_trade['pnl']:+,.2f} USDT")
            print(f"   Chiến lược: {worst_trade['strategy']}")
            print(f"   Thời gian: {worst_trade['entry_time']} -> {worst_trade['exit_time']}")
        
        # Thống kê theo chiến lược
        strategy_stats = {}
        for trade in trades:
            strategy = trade['strategy']
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'trades': 0, 'pnl': 0, 'wins': 0}
            
            strategy_stats[strategy]['trades'] += 1
            strategy_stats[strategy]['pnl'] += trade['pnl']
            if trade['pnl'] > 0:
                strategy_stats[strategy]['wins'] += 1
        
        print(f"\n📊 THỐNG KÊ THEO CHIẾN LƯỢC:")
        for strategy, stats in strategy_stats.items():
            win_rate = (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0
            print(f"   {strategy}: {stats['trades']} lệnh, {stats['pnl']:+,.2f} USDT, {win_rate:.1f}% thắng")
    
    print("=" * 70)

def save_results_to_csv(results, filename=None):
    """Lưu kết quả ra file CSV"""
    if not results or not results['trades']:
        print("❌ Không có dữ liệu để lưu!")
        return
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_results_{timestamp}.csv"
    
    trades_df = pd.DataFrame(results['trades'])
    
    # Thêm thông tin tổng quan
    summary_data = {
        'Metric': ['Initial Balance', 'Final Balance', 'Total Return (%)', 'Total Trades', 
                  'Winning Trades', 'Losing Trades', 'Win Rate (%)', 'Total PnL', 
                  'Average PnL', 'Profit Factor', 'Max Drawdown (%)', 'Sharpe Ratio'],
        'Value': [results.get('initial_balance', 0), results['final_balance'], 
                 results['total_return'], results['metrics']['total_trades'],
                 results['metrics']['winning_trades'], results['metrics']['losing_trades'],
                 results['metrics']['win_rate'], results['metrics']['total_pnl'],
                 results['metrics']['average_pnl'], results['metrics']['profit_factor'],
                 results['metrics']['max_drawdown'], results['metrics']['sharpe_ratio']]
    }
    
    summary_df = pd.DataFrame(summary_data)
    
    # Lưu ra file
    with pd.ExcelWriter(filename.replace('.csv', '.xlsx'), engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        trades_df.to_excel(writer, sheet_name='Trades', index=False)
    
    print(f"💾 Kết quả đã lưu vào: {filename.replace('.csv', '.xlsx')}")

def main():
    """Main function"""
    print_banner()
    
    # Lấy input từ user
    config = get_user_input()
    if not config:
        print("❌ Cấu hình không hợp lệ!")
        return
    
    # Chạy backtest
    results = run_backtest_with_progress(config)
    
    if results:
        # In kết quả
        print_detailed_results(results)
        
        # Hỏi có muốn lưu kết quả không
        save_choice = input("\n💾 Có muốn lưu kết quả ra file không? (y/n): ").lower()
        if save_choice == 'y':
            save_results_to_csv(results)
        
        # Hỏi có muốn chạy backtest khác không
        again_choice = input("\n🔄 Có muốn chạy backtest khác không? (y/n): ").lower()
        if again_choice == 'y':
            main()
    else:
        print("❌ Backtest thất bại! Vui lòng thử lại.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Backtest đã dừng bởi user")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        print("Vui lòng kiểm tra lại cấu hình và thử lại.")
