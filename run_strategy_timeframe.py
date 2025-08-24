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

def run_strategy_with_timeframe(strategy_name, timeframe, symbol='BTCUSDT', start_date=None, end_date=None, initial_balance=10000, atr_multiplier=None, reward_ratio=None, trailing_ratio=None, is_reverse=False, show_history_balance=False, enable_scaling=False, scaling_threshold=1.0, scaling_multiplier=2.0, no_fees=False):
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
        # elif strategy_name == 'divergence_strategy':
        #     strategy_parts = ['divergence_strategy']
        #     if is_reverse:
        #         strategy_parts.append('reverse')
        #     strategy_name = '_'.join(strategy_parts)
        # elif strategy_name == 'simple_divergence_strategy':
        #     strategy_parts = ['simple_divergence_strategy']
        #     if is_reverse:
        #         strategy_parts.append('reverse')
        #     strategy_name = '_'.join(strategy_parts)
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
    
    # Get symbol info
    from config import TradingConfig
    symbol_info = TradingConfig.get_symbol_info(symbol)
    
    print(f"🎯 RUNNING STRATEGY: {strategy_name}")
    print(f"🪙 SYMBOL: {symbol} ({symbol_info['name']})")
    print(f"🕐 TIMEFRAME: {timeframe}")
    
    # Display trading fee information
    from config import TradingConfig
    fee_info = TradingConfig.get_trading_fee_info(symbol, no_fees)
    if no_fees:
        print(f"💰 Trading Fee: DISABLED (no fees)")
    elif fee_info['fee_type'] == 'fixed':
        print(f"💰 Trading Fee: ${fee_info['fee_per_btc']:.1f} per BTC")
    else:
        print(f"💰 Trading Fee: {fee_info['fee_rate']*100:.1f}%")
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
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
    if end_date is None:
        end_date = datetime.strptime('2025-08-22', '%Y-%m-%d')
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    print(f"📅 Test period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"💰 Initial balance: ${initial_balance:,.0f} USDT")
    print("=" * 60)
    
    try:
        strategy_results = backtester.run_backtest(
            symbol=symbol,
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_balance=initial_balance,
            timeframe=timeframe,
            enable_scaling=enable_scaling,
            scaling_threshold=scaling_threshold,
            scaling_multiplier=scaling_multiplier,
            no_fees=no_fees,
            reward_ratio=reward_ratio if reward_ratio is not None else 3.0
        )
        
        if strategy_results:
            metrics = strategy_results.get('metrics', {})
            
            print(f"\n📊 RESULTS:")
            print("-" * 40)
            print(f"✅ Completed: {metrics.get('total_trades', 0)} trades")
            print(f"📈 Final Balance: ${strategy_results.get('final_balance', 10000):,.2f}")
            print(f"💰 Savings Account: ${strategy_results.get('savings_account', 0):,.2f}")
            print(f"💎 Total Wealth: ${strategy_results.get('total_wealth', 0):,.2f}")
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
            
            # Export balance history to file if enabled
            if show_history_balance:
                balance_history = strategy_results.get('balance_history', [])
                if balance_history:
                    # Generate filename with timestamp and organize by symbol/strategy
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Create directory structure: histories/symbol/strategy_name/
                    import os
                    strategy_dir = f"histories/{symbol}/{strategy_name}"
                    os.makedirs(strategy_dir, exist_ok=True)
                    
                    filename = f"{strategy_dir}/{timeframe}_{timestamp}.md"
                    
                    # Create markdown content
                    md_content = f"""# Balance History Report

## Strategy Information
- **Strategy**: {strategy_name}
- **Timeframe**: {timeframe}
- **Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
- **Initial Balance**: ${initial_balance:,.2f}
- **Final Balance**: ${strategy_results.get('final_balance', 0):,.2f}
- **Savings Account**: ${strategy_results.get('savings_account', 0):,.2f}
- **Total Wealth**: ${strategy_results.get('total_wealth', 0):,.2f}
- **Total Return**: {strategy_results.get('total_return', 0):.2f}%
- **Total Trades**: {len(balance_history)}
- **Win Rate**: {strategy_results.get('metrics', {}).get('win_rate', 0):.2f}%
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Trading Parameters
- **ATR Multiplier**: {atr_multiplier if atr_multiplier else 'Default'}
- **Reward Ratio**: {reward_ratio if reward_ratio else 'Default'}
- **Trailing Ratio**: {trailing_ratio if trailing_ratio else 'Default'}
- **Reverse Signal**: {'Yes' if is_reverse else 'No'}
- **Position Scaling**: {'Yes' if enable_scaling else 'No'}
- **Scaling Threshold**: {scaling_threshold if enable_scaling else 'N/A'}
- **Scaling Multiplier**: {scaling_multiplier if enable_scaling else 'N/A'}

## Balance History

| Trade # | Date | Type | Entry | Exit | SL | TP | Size | PnL | Balance | Return% | Scaling |
|---------|------|------|-------|------|----|----|----|-----|---------|---------|---------|
"""
                    
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
                        
                        md_content += f"| {i} | {date} | {trade_type} | ${entry_price:.2f} | ${exit_price:.2f} | ${stop_loss:.2f} | ${take_profit:.2f} | {position_size:.4f} | ${pnl:.2f} | ${balance:.2f} | {return_pct:.2f}% | {scaling_details} |\n"
                    
                    # Add summary statistics
                    md_content += f"""
## Summary Statistics

### Performance Metrics
- **Total Trades**: {len(balance_history)}
- **Winning Trades**: {strategy_results.get('metrics', {}).get('winning_trades', 0)}
- **Losing Trades**: {strategy_results.get('metrics', {}).get('losing_trades', 0)}
- **Win Rate**: {strategy_results.get('metrics', {}).get('win_rate', 0):.2f}%
- **Profit Factor**: {strategy_results.get('metrics', {}).get('profit_factor', 0):.2f}
- **Max Drawdown**: {strategy_results.get('metrics', {}).get('max_drawdown', 0):.2f}%
- **Sharpe Ratio**: {strategy_results.get('metrics', {}).get('sharpe_ratio', 0):.2f}

### Exit Analysis
- **Stop Loss**: {strategy_results.get('exit_counters', {}).get('stop_loss', 0)} trades
- **Stop Loss at Entry**: {strategy_results.get('exit_counters', {}).get('stop_loss_at_entry', 0)} trades
- **Take Profit**: {strategy_results.get('exit_counters', {}).get('take_profit', 0)} trades

### Account Status
- **Final Balance**: ${strategy_results.get('final_balance', 0):,.2f}
- **Savings Account**: ${strategy_results.get('savings_account', 0):,.2f}
- **Total Wealth**: ${strategy_results.get('total_wealth', 0):,.2f}
- **Total Return**: {strategy_results.get('total_return', 0):.2f}%
- **Account Blown**: {'Yes' if strategy_results.get('account_blown', False) else 'No'}

---
*Generated by BTC Strategy Backtester*
"""
                    
                    # Write to file
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(md_content)
                        print(f"\n📊 BALANCE HISTORY: Exported to {filename}")
                    except Exception as e:
                        print(f"\n❌ Error exporting balance history: {e}")
                else:
                    print(f"\n📊 BALANCE HISTORY: No trades to export")
                
        else:
            print("❌ Strategy failed: No results")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run trading strategy with specific timeframe and date range')
    parser.add_argument('strategy', help='Strategy name (e.g., ema_rsi, ultra_simple_strategy)')
    parser.add_argument('timeframe', help='Timeframe (5m, 15m, 30m, 1h, 2h, 4h)')
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading symbol (BTCUSDT, SUIUSDT)')
    parser.add_argument('--start_date', default='2025-08-15', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', default='2025-08-22', help='End date (YYYY-MM-DD)')
    parser.add_argument('--balance', type=float, default=10000, help='Initial balance')
    parser.add_argument('--atr_multiplier', type=float, help='ATR multiplier for stop loss (e.g., 1.0, 1.5, 2.0)')
    parser.add_argument('--reward_ratio', type=float, help='Risk:Reward ratio for take profit (e.g., 2.0, 3.0, 4.0)')
    parser.add_argument('--trailing_ratio', type=float, help='Risk:Reward ratio for trailing stop (e.g., 1.0, 1.5, 2.0)')
    parser.add_argument('--is_reverse', type=int, choices=[0, 1], default=0, help='Reverse signal (0=normal, 1=reverse TP↔SL)')
    parser.add_argument('--show_history_balance', type=int, choices=[0, 1], default=0, help='Export balance history to file (0=no, 1=yes)')
    parser.add_argument('--enable_scaling', type=int, choices=[0, 1], default=0, help='Enable position scaling when profitable (0=no, 1=yes)')
    parser.add_argument('--scaling_threshold', type=float, default=1.0, help='R:R threshold to start scaling (e.g., 1.0, 1.5, 2.0)')
    parser.add_argument('--scaling_multiplier', type=float, default=2.0, help='Risk multiplier when scaling (e.g., 2.0 for 2R, 3.0 for 3R)')
    parser.add_argument('--no_fees', type=int, choices=[0, 1], default=0, help='Disable trading fees (0=normal fees, 1=no fees)')
    
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
        print("🪙 Available symbols:")
        symbols = ['BTCUSDT', 'SUIUSDT']
        for sym in symbols:
            print(f"   - {sym}")
        
        print("")
        print("📝 Examples:")
        print("   python run_strategy_timeframe.py ema_rsi 5m")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 1h --symbol SUIUSDT")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 2h --symbol BTCUSDT --atr_multiplier 1.0 --reward_ratio 2.0")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 1h --symbol SUIUSDT --start_date 2025-07-01 --end_date 2025-08-01")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 5m --balance 50000 --atr_multiplier 0.8")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --reward_ratio 4.0 --trailing_ratio 1.5")
        print("   python run_strategy_timeframe.py smc_strategy 1h --is_reverse 1")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --is_reverse 1 --reward_ratio 2.0")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --show_history_balance 1")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --enable_scaling 1 --scaling_threshold 1.5 --scaling_multiplier 2.0")
        print("   python run_strategy_timeframe.py ultra_simple_strategy 15m --no_fees 1")
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
        print("   --show_history_balance: Export balance history to file (0=no, 1=yes)")
        print("   • When enabled: Export detailed balance history to .md file in histories/ folder")
        print("   • Useful for: Detailed analysis, debugging, performance tracking, record keeping")
        print("")
        print("📈 Position Scaling Parameters:")
        print("   --enable_scaling: Enable position scaling when profitable (0=no, 1=yes)")
        print("   --scaling_threshold: R:R threshold to start scaling (e.g., 1.0, 1.5, 2.0)")
        print("   --scaling_multiplier: Risk multiplier when scaling (e.g., 2.0 for 2R, 3.0 for 3R)")
        print("   • When enabled: Increase position size when account is profitable")
        print("   • Useful for: Maximizing profits, aggressive trading, momentum strategies")
        print("")
        print("💰 Trading Fee Parameters:")
        print("   --no_fees: Disable trading fees (0=normal fees, 1=no fees)")
        print("   • When enabled: No trading fees applied to PnL calculations")
        print("   • Useful for: Testing without fees, comparing fee impact, fee-free exchanges")
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
        symbol=args.symbol,
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
        scaling_multiplier=args.scaling_multiplier,
        no_fees=args.no_fees
    )

if __name__ == "__main__":
    main()
