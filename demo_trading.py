#!/usr/bin/env python3
"""
Demo Trading System
Test with data that has signals
"""

import os
import shutil
from datetime import datetime, timedelta
from real_time_trader import RealTimeTrader

def demo_trading():
    """Demo trading with multiple cycles"""
    
    # Clean up existing data
    if os.path.exists('real_time_data'):
        shutil.rmtree('real_time_data')
    
    print("🤖 DEMO TRADING SYSTEM")
    print("="*50)
    
    # Initialize trader with no fees
    trader = RealTimeTrader(
        symbol='SUIUSDT',
        initial_balance=1000,
        strategy_name='ultra_simple_strategy',
        no_fees=True
    )
    
    # Test with different time periods to find signals
    test_periods = [
        (datetime(2025, 8, 1, 10, 0, 0), datetime(2025, 8, 1, 14, 0, 0)),
        (datetime(2025, 8, 2, 8, 0, 0), datetime(2025, 8, 2, 12, 0, 0)),
        (datetime(2025, 8, 3, 6, 0, 0), datetime(2025, 8, 3, 10, 0, 0)),
        (datetime(2025, 8, 4, 4, 0, 0), datetime(2025, 8, 4, 8, 0, 0)),
        (datetime(2025, 8, 5, 2, 0, 0), datetime(2025, 8, 5, 6, 0, 0)),
    ]
    
    for i, (start_date, end_date) in enumerate(test_periods, 1):
        print(f"\n🔄 Cycle {i}: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Override the data fetching method for this demo
        def get_demo_data(self, timeframe='5m', limit=100):
            """Get demo market data"""
            try:
                data = self.backtester._fetch_historical_data(
                    self.symbol, start_date, end_date, timeframe
                )
                
                if data.empty:
                    return None
                
                # Add indicators
                data = self.backtester._add_indicators(data)
                return data
                
            except Exception as e:
                print(f"Error getting demo data: {e}")
                return None
        
        # Replace the method temporarily
        trader.get_current_market_data = get_demo_data.__get__(trader, RealTimeTrader)
        
        # Run trading cycle
        trader.run_trading_cycle()
        
        # Print summary
        summary = trader.get_trading_summary()
        print(f"   Balance: ${summary['current_balance']:.2f}")
        print(f"   Savings: ${summary['savings_account']:.2f}")
        print(f"   Trades: {summary['total_trades']}")
        print(f"   Position: {'Open' if summary['open_position'] else 'None'}")
    
    # Final summary
    print("\n" + "="*50)
    print("📊 FINAL DEMO SUMMARY")
    print("="*50)
    
    final_summary = trader.get_trading_summary()
    print(f"Initial Balance: ${final_summary['initial_balance']:.2f}")
    print(f"Final Balance: ${final_summary['current_balance']:.2f}")
    print(f"Savings Account: ${final_summary['savings_account']:.2f}")
    print(f"Total Wealth: ${final_summary['total_wealth']:.2f}")
    print(f"Total Return: {final_summary['total_return']:.2f}%")
    print(f"Total Trades: {final_summary['total_trades']}")
    print(f"Win Rate: {final_summary['win_rate']:.1f}%")
    
    if final_summary['total_trades'] > 0:
        print("\n📈 Recent Trades:")
        for trade in trader.trade_history[-5:]:
            time_str = datetime.fromisoformat(trade['exit_time']).strftime('%H:%M')
            print(f"   {time_str} - {trade['side'].upper()} - ${trade['pnl']:.2f} - {trade['exit_type']}")
    
    print("\n✅ Demo completed! Check real_time_data/ folder for saved data.")

if __name__ == "__main__":
    demo_trading()
