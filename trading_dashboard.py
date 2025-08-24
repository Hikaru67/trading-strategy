#!/usr/bin/env python3
"""
Trading Dashboard
View real-time trading system status and history
"""

import os
import json
import sys
from datetime import datetime
from real_time_trader import RealTimeTrader

def print_dashboard():
    """Print trading dashboard"""
    try:
        trader = RealTimeTrader(
            symbol='SUIUSDT',
            initial_balance=1000,
            strategy_name='ultra_simple_strategy'
        )
        
        summary = trader.get_trading_summary()
        
        print("\n" + "="*80)
        print("🤖 REAL-TIME TRADING DASHBOARD")
        print("="*80)
        print(f"📅 Last Updated: {summary['last_updated']}")
        print(f"🪙 Symbol: SUIUSDT")
        print(f"📊 Strategy: ultra_simple_strategy")
        print()
        
        # Balance section
        print("💰 ACCOUNT BALANCE")
        print("-" * 40)
        print(f"Initial Balance:     ${summary['initial_balance']:>10,.2f}")
        print(f"Current Balance:     ${summary['current_balance']:>10,.2f}")
        print(f"Savings Account:     ${summary['savings_account']:>10,.2f}")
        print(f"Total Wealth:        ${summary['total_wealth']:>10,.2f}")
        print(f"Total Return:        {summary['total_return']:>10,.2f}%")
        print()
        
        # Trading performance
        print("📊 TRADING PERFORMANCE")
        print("-" * 40)
        print(f"Total Trades:        {summary['total_trades']:>10}")
        print(f"Winning Trades:      {summary['winning_trades']:>10}")
        print(f"Losing Trades:       {summary['losing_trades']:>10}")
        print(f"Win Rate:            {summary['win_rate']:>10,.1f}%")
        print()
        
        # Current position
        print("📋 CURRENT POSITION")
        print("-" * 40)
        if summary['open_position']:
            position = trader.open_position
            print(f"Status:              {'OPEN':>10}")
            print(f"Side:                {position['side'].upper():>10}")
            print(f"Entry Price:         ${position['entry_price']:>10,.4f}")
            print(f"Stop Loss:           ${position['stop_loss']:>10,.4f}")
            print(f"Take Profit:         ${position['take_profit']:>10,.4f}")
            print(f"Position Size:       {position['position_size']:>10,.4f}")
            print(f"Scaling Multiplier:  {position['scaling_info']['multiplier']:>10}x")
        else:
            print(f"Status:              {'NONE':>10}")
        print()
        
        # Recent trades
        print("📈 RECENT TRADES (Last 10)")
        print("-" * 80)
        if trader.trade_history:
            print(f"{'Time':<20} {'Side':<6} {'Entry':<10} {'Exit':<10} {'PnL':<10} {'Type':<12}")
            print("-" * 80)
            
            for trade in trader.trade_history[-10:]:
                time_str = datetime.fromisoformat(trade['exit_time']).strftime('%Y-%m-%d %H:%M')
                side = trade['side'].upper()
                entry = f"${trade['entry_price']:.4f}"
                exit_price = f"${trade['exit_price']:.4f}"
                pnl = f"${trade['pnl']:.2f}"
                exit_type = trade['exit_type']
                
                print(f"{time_str:<20} {side:<6} {entry:<10} {exit_price:<10} {pnl:<10} {exit_type:<12}")
        else:
            print("No trades yet")
        print()
        
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")

def print_equity_chart():
    """Print simple equity chart"""
    try:
        trader = RealTimeTrader(
            symbol='SUIUSDT',
            initial_balance=1000,
            strategy_name='ultra_simple_strategy'
        )
        
        if not trader.equity_curve:
            print("No equity data available")
            return
        
        print("\n📈 EQUITY CURVE (Last 20 points)")
        print("-" * 60)
        print(f"{'Time':<20} {'Balance':<10} {'Savings':<10} {'Total':<10} {'Return':<10}")
        print("-" * 60)
        
        for point in trader.equity_curve[-20:]:
            time_str = datetime.fromisoformat(point['time']).strftime('%m-%d %H:%M')
            balance = f"${point['balance']:.0f}"
            savings = f"${point['savings_account']:.0f}"
            total = f"${point['total_wealth']:.0f}"
            return_pct = ((point['total_wealth'] - 1000) / 1000) * 100
            return_str = f"{return_pct:.1f}%"
            
            print(f"{time_str:<20} {balance:<10} {savings:<10} {total:<10} {return_str:<10}")
        
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error loading equity chart: {e}")

def print_trade_details():
    """Print detailed trade information"""
    try:
        trader = RealTimeTrader(
            symbol='SUIUSDT',
            initial_balance=1000,
            strategy_name='ultra_simple_strategy'
        )
        
        if not trader.trade_history:
            print("No trades available")
            return
        
        print("\n📋 DETAILED TRADE HISTORY")
        print("="*120)
        
        for i, trade in enumerate(trader.trade_history[-20:], 1):
            print(f"\nTrade #{len(trader.trade_history) - 20 + i}")
            print("-" * 50)
            print(f"Entry Time:    {trade['entry_time']}")
            print(f"Exit Time:     {trade['exit_time']}")
            print(f"Side:          {trade['side'].upper()}")
            print(f"Entry Price:   ${trade['entry_price']:.4f}")
            print(f"Exit Price:    ${trade['exit_price']:.4f}")
            print(f"Stop Loss:     ${trade['stop_loss']:.4f}")
            print(f"Take Profit:   ${trade['take_profit']:.4f}")
            print(f"Position Size: {trade['position_size']:.4f}")
            print(f"Exit Type:     {trade['exit_type']}")
            print(f"PnL:           ${trade['pnl']:.2f}")
            print(f"Fee:           ${trade['fee']:.2f}")
            print(f"Balance:       ${trade['balance']:.2f}")
            print(f"Savings:       ${trade['savings_account']:.2f}")
            
            if trade.get('scaling_info'):
                scaling = trade['scaling_info']
                print(f"Scaling:       {scaling['multiplier']}x")
        
        print("\n" + "="*120)
        
    except Exception as e:
        print(f"❌ Error loading trade details: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python trading_dashboard.py dashboard    - Show main dashboard")
        print("  python trading_dashboard.py equity       - Show equity chart")
        print("  python trading_dashboard.py trades       - Show detailed trades")
        print("  python trading_dashboard.py all          - Show everything")
        return
    
    command = sys.argv[1].lower()
    
    if command == "dashboard":
        print_dashboard()
    elif command == "equity":
        print_equity_chart()
    elif command == "trades":
        print_trade_details()
    elif command == "all":
        print_dashboard()
        print_equity_chart()
        print_trade_details()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
