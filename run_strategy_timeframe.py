#!/usr/bin/env python3
"""
Run strategy with flexible timeframe
Usage: python run_strategy_timeframe.py <strategy_name> <timeframe>
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest import Backtester
from datetime import datetime
import argparse

def run_strategy_with_timeframe(strategy_name, timeframe, start_date=None, end_date=None, initial_balance=10000, atr_multiplier=None, reward_ratio=None, trailing_ratio=None, is_reverse=False, show_history_balance=False, enable_scaling=False, scaling_threshold=1.0, scaling_multiplier=2.0):
    """Run a specific strategy with specified timeframe and date range"""
    
    # Build strategy name with parameters if provided
    if atr_multiplier is not None or reward_ratio is not None or trailing_ratio is not None or is_reverse:
        if strategy_name == 'ultra_simple_strategy':
            strategy_parts = ['ultra_simple_strategy']
            if atr_multiplier is not None:
                strategy_parts.append(f'atr{atr_multiplier}')
            if reward_ratio is not None:
                strategy_parts.append(f'rr{reward_ratio}')
            if trailing_ratio is not None:
                strategy_parts.append(f'trail{trailing_ratio}')
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'smc_strategy':
            strategy_parts = ['smc_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'ema_rsi':
            strategy_parts = ['ema_rsi']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'bollinger_stochastic':
            strategy_parts = ['bollinger_stochastic']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'macd_vwap':
            strategy_parts = ['macd_vwap']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'ichimoku':
            strategy_parts = ['ichimoku']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'vsa_obv':
            strategy_parts = ['vsa_obv']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'multi_indicator':
            strategy_parts = ['multi_indicator']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'ema_rsi_ichimoku':
            strategy_parts = ['ema_rsi_ichimoku']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'enhanced_with_candlestick':
            strategy_parts = ['enhanced_with_candlestick']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'divergence_strategy':
            strategy_parts = ['divergence_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'simple_divergence_strategy':
            strategy_parts = ['simple_divergence_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'wyckoff_vsa':
            strategy_parts = ['wyckoff_vsa']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'practical_wyckoff_vsa':
            strategy_parts = ['practical_wyckoff_vsa']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'simple_test_strategy':
            strategy_parts = ['simple_test_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'smart_tp_strategy':
            strategy_parts = ['smart_tp_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'adaptive_tp_strategy':
            strategy_parts = ['adaptive_tp_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
        elif strategy_name == 'breaker_block_strategy':
            strategy_parts = ['breaker_block_strategy']
            if is_reverse:
                strategy_parts.append('reverse')
            strategy_name = '_'.join(strategy_parts)
    
    print(f"🎯 RUNNING STRATEGY: {strategy_name}")
    print(f"🕐 TIMEFRAME: {timeframe}")
    if atr_multiplier is not None:
        print(f"📊 ATR Multiplier: {atr_multiplier}")
    if reward_ratio is not None:
        print(f"🎯 Risk:Reward Ratio: 1:{reward_ratio}")
    if trailing_ratio is not None:
        print(f"⚖️  Trailing Stop Ratio: 1:{trailing_ratio}")
    if is_reverse:
        print(f"🔄 REVERSE SIGNAL: Enabled (TP ↔ SL swap)")
    if show_history_balance:
        print(f"📊 BALANCE HISTORY: Enabled (show after each trade)")
    if enable_scaling:
        print(f"📈 POSITION SCALING: Enabled (start at {scaling_threshold}R, scale to {scaling_multiplier}R)")
    print("=" * 60)
    
    # Create backtester
    backtester = Backtester()
    
    # Use provided dates or defaults
    if start_date is None:
        start_date = datetime.strptime('2025-08-15', '%Y-%m-%d')
    if end_date is None:
        end_date = datetime.strptime('2025-08-22', '%Y-%m-%d')
    
    print(f"📅 Test period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"💰 Initial balance: ${initial_balance:,.0f} USDT")
    print("=" * 60)
    
    try:
        strategy_results = backtester.run_backtest(
            symbol='BTCUSDT',
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_balance=initial_balance,
            timeframe=timeframe,
            enable_scaling=enable_scaling,
            scaling_threshold=scaling_threshold,
            scaling_multiplier=scaling_multiplier
        )
        
        if strategy_results:
            metrics = strategy_results.get('metrics', {})
            
            print(f"\n📊 RESULTS:")
            print("-" * 40)
            print(f"✅ Completed: {metrics.get('total_trades', 0)} trades")
            print(f"📈 Final Balance: ${strategy_results.get('final_balance', 10000):,.2f}")
            print(f"📊 Total Return: {strategy_results.get('total_return', 0):.2f}%")
            print(f"🎯 Win Rate: {metrics.get('win_rate', 0):.2f}%")
            print(f"📉 Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
            print(f"📊 Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"📈 Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"💰 Avg Trade: ${metrics.get('avg_trade', 0):,.2f}")
            print(f"📊 Avg R:R: {metrics.get('avg_rr', 0):.2f}")
            
            # Display exit counters
            exit_counters = strategy_results.get('exit_counters', {})
            print(f"\n📈 EXIT ANALYSIS:")
            print("-" * 40)
            print(f"🛑 Stop Loss: {exit_counters.get('stop_loss', 0)} trades")
            print(f"⚖️  Stop Loss at Entry: {exit_counters.get('stop_loss_at_entry', 0)} trades")
            print(f"🎯 Take Profit: {exit_counters.get('take_profit', 0)} trades")
            
            total_exits = sum(exit_counters.values())
            if total_exits > 0:
                sl_pct = (exit_counters.get('stop_loss', 0) / total_exits) * 100
                sl_entry_pct = (exit_counters.get('stop_loss_at_entry', 0) / total_exits) * 100
                tp_pct = (exit_counters.get('take_profit', 0) / total_exits) * 100
                print(f"📊 Exit Distribution: SL {sl_pct:.1f}% | SL@Entry {sl_entry_pct:.1f}% | TP {tp_pct:.1f}%")
            
            # Performance assessment
            total_trades = metrics.get('total_trades', 0)
            win_rate = metrics.get('win_rate', 0)
            total_return = strategy_results.get('total_return', 0)
            
            print(f"\n🎭 PERFORMANCE ASSESSMENT:")
            print("-" * 40)
            
            if total_trades == 0:
                print("❌ No trades generated - strategy too conservative")
                print("💡 Try shorter timeframes (5m, 15m) for more signals")
            elif total_trades < 5:
                print("⚠️  Low trade frequency - may need parameter adjustment")
            else:
                print("✅ Good trade frequency")
            
            if win_rate >= 50:
                print("✅ Good win rate")
            elif win_rate >= 30:
                print("⚠️  Moderate win rate")
            else:
                print("❌ Low win rate - needs optimization")
            
            # Check if account was blown
            account_blown = strategy_results.get('account_blown', False)
            
            if account_blown:
                print("🔥 ACCOUNT BLOWN! Trading stopped due to insufficient funds")
            elif total_return > 0:
                print("✅ Profitable strategy")
            else:
                print("❌ Unprofitable strategy")
            
            # Display balance history if enabled
            if show_history_balance:
                balance_history = strategy_results.get('balance_history', [])
                if balance_history:
                    print(f"\n📊 BALANCE HISTORY:")
                    print("-" * 140)
                    print(f"{'Trade #':<8} {'Date':<20} {'Type':<6} {'Entry':<10} {'Exit':<10} {'SL':<10} {'TP':<10} {'Size':<8} {'PnL':<10} {'Balance':<12} {'Return%':<8} {'Scaling':<15}")
                    print("-" * 140)
                    
                    for i, trade in enumerate(balance_history, 1):
                        trade_type = trade.get('type', 'N/A')
                        entry_price = trade.get('entry_price', 0)
                        exit_price = trade.get('exit_price', 0)
                        stop_loss = trade.get('stop_loss', 0)
                        take_profit = trade.get('take_profit', 0)
                        position_size = trade.get('position_size', 0)
                        pnl = trade.get('pnl', 0)
                        balance = trade.get('balance', initial_balance)
                        return_pct = ((balance - initial_balance) / initial_balance) * 100
                        date = trade.get('date', 'N/A')
                        scaling_details = trade.get('scaling_details', '')
                        
                        print(f"{i:<8} {date:<20} {trade_type:<6} ${entry_price:<9.2f} ${exit_price:<9.2f} ${stop_loss:<9.2f} ${take_profit:<9.2f} {position_size:<8.4f} ${pnl:<9.2f} ${balance:<11.2f} {return_pct:<8.2f} {scaling_details}")
                    
                    print("-" * 140)
                else:
                    print(f"\n📊 BALANCE HISTORY: No trades to display")
                
        else:
            print("❌ Strategy failed: No results")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run trading strategy with specific timeframe and date range')
    parser.add_argument('strategy', help='Strategy name (e.g., ema_rsi, ultra_simple_strategy)')
    parser.add_argument('timeframe', help='Timeframe (5m, 15m, 30m, 1h, 2h, 4h)')
    parser.add_argument('--start_date', default='2025-08-15', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', default='2025-08-22', help='End date (YYYY-MM-DD)')
    parser.add_argument('--balance', type=float, default=10000, help='Initial balance')
    parser.add_argument('--atr_multiplier', type=float, help='ATR multiplier for stop loss (e.g., 1.0, 1.5, 2.0)')
    parser.add_argument('--reward_ratio', type=float, help='Risk:Reward ratio for take profit (e.g., 2.0, 3.0, 4.0)')
    parser.add_argument('--trailing_ratio', type=float, help='Risk:Reward ratio for trailing stop (e.g., 1.0, 1.5, 2.0)')
    parser.add_argument('--is_reverse', type=int, choices=[0, 1], default=0, help='Reverse signal (0=normal, 1=reverse TP↔SL)')
    parser.add_argument('--show_history_balance', type=int, choices=[0, 1], default=0, help='Show balance history after each trade (0=no, 1=yes)')
    parser.add_argument('--enable_scaling', type=int, choices=[0, 1], default=0, help='Enable position scaling when profitable (0=no, 1=yes)')
    parser.add_argument('--scaling_threshold', type=float, default=1.0, help='R:R threshold to start scaling (e.g., 1.0, 1.5, 2.0)')
    parser.add_argument('--scaling_multiplier', type=float, default=2.0, help='Risk multiplier when scaling (e.g., 2.0 for 2R, 3.0 for 3R)')
    
    # Check if arguments provided
    if len(sys.argv) < 3:
        print("🚀 STRATEGY TIMEFRAME TESTER")
        print("=" * 50)
        print("Usage: python run_strategy_timeframe.py <strategy> <timeframe> [options]")
        print("")
        print("📊 Available strategies:")
        strategies = [
            'ultra_simple_strategy',
            'ema_rsi', 
            'bollinger_stochastic',
            'macd_vwap',
            'ichimoku',
            'vsa_obv',
            'multi_indicator',
            'ema_rsi_ichimoku',
            'enhanced_with_candlestick',
            'simple_divergence_strategy',
            'divergence_strategy',
            'wyckoff_vsa',
            'practical_wyckoff_vsa'
        ]
        
        for strategy in strategies:
            print(f"   - {strategy}")
        
        print("")
        print("🕐 Available timeframes:")
        timeframes = ['5m', '15m', '30m', '1h', '2h', '4h']
        for tf in timeframes:
            print(f"   - {tf}")
        
        print("")
        print("📝 Examples:")
        print("   python run_strategy_timeframe.py ema_rsi 5m")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 1h")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 2h --atr_multiplier 1.0 --reward_ratio 2.0")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 1h --start_date 2025-07-01 --end_date 2025-08-01")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 5m --balance 50000 --atr_multiplier 0.8")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --reward_ratio 4.0 --trailing_ratio 1.5")
        print("   python run_strategy_timeframe.py smc_strategy 1h --is_reverse 1")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --is_reverse 1 --reward_ratio 2.0")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --show_history_balance 1")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --enable_scaling 1 --scaling_threshold 1.5 --scaling_multiplier 2.0")
        print("")
        print("🎯 R:R Parameters for ultra_simple_strategy:")
        print("   --atr_multiplier: ATR multiplier for stop loss (default: 1.5)")
        print("   --reward_ratio: Risk:Reward ratio for take profit (default: 3.0)")
        print("   --trailing_ratio: Risk:Reward ratio for trailing stop (default: 1.0)")
        print("")
        print("🔄 Reverse Signal Parameters:")
        print("   --is_reverse: Reverse signal direction (0=normal, 1=reverse)")
        print("   • When enabled: LONG↔SHORT, TP↔SL swap")
        print("   • Useful for: SMC strategy, testing contrarian signals")
        print("")
        print("📊 Balance History Parameters:")
        print("   --show_history_balance: Show balance after each trade (0=no, 1=yes)")
        print("   • When enabled: Display balance history after each trade")
        print("   • Useful for: Detailed analysis, debugging, performance tracking")
        print("")
        print("📈 Position Scaling Parameters:")
        print("   --enable_scaling: Enable position scaling when profitable (0=no, 1=yes)")
        print("   --scaling_threshold: R:R threshold to start scaling (e.g., 1.0, 1.5, 2.0)")
        print("   --scaling_multiplier: Risk multiplier when scaling (e.g., 2.0 for 2R, 3.0 for 3R)")
        print("   • When enabled: Increase position size when account is profitable")
        print("   • Useful for: Maximizing profits, aggressive trading, momentum strategies")
        return
    
    args = parser.parse_args()
    
    # Validate timeframe
    valid_timeframes = ['5m', '15m', '30m', '1h', '2h', '4h']
    if args.timeframe not in valid_timeframes:
        print(f"❌ Invalid timeframe: {args.timeframe}")
        print(f"Valid timeframes: {', '.join(valid_timeframes)}")
        return
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError as e:
        print(f"❌ Invalid date format: {e}")
        print("Use YYYY-MM-DD format (e.g., 2025-08-15)")
        return
    
    # Validate date range
    if start_date >= end_date:
        print("❌ Start date must be before end date")
        return
    
    # Run the strategy
    run_strategy_with_timeframe(
        args.strategy, 
        args.timeframe, 
        start_date=start_date,
        end_date=end_date,
        initial_balance=args.balance,
        atr_multiplier=args.atr_multiplier,
        reward_ratio=args.reward_ratio,
        trailing_ratio=args.trailing_ratio,
        is_reverse=args.is_reverse,
        show_history_balance=args.show_history_balance,
        enable_scaling=args.enable_scaling,
        scaling_threshold=args.scaling_threshold,
        scaling_multiplier=args.scaling_multiplier
    )

if __name__ == "__main__":
    main()
