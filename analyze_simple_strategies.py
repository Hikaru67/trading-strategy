#!/usr/bin/env python3
"""
Analyze Simple Strategies with Fixed Parameters
"""

import os
import sys
import pandas as pd
from datetime import datetime
from run_strategy_timeframe import run_strategy_with_timeframe
from config import TradingConfig

def get_simple_strategies():
    """Get list of simple and stable strategies"""
    strategies = [
        # Basic strategies (most stable)
        'ema_rsi', 'bollinger_stochastic', 'macd_vwap', 'ichimoku',
        # Advanced strategies (tested)
        'vsa_obv', 'multi_indicator', 'ema_rsi_ichimoku',
        # Ultra simple
        'ultra_simple_strategy'
    ]
    return strategies

def analyze_simple_strategies(symbol='SUIUSDT', start_date='2025-01-01', end_date='2025-08-22',
                             initial_balance=1000, reward_ratio=1.0, is_reverse=True,
                             no_fees=True, trailing_ratio=0, enable_scaling=True, 
                             scaling_multiplier=1.0, timeframes=['5m', '15m', '30m', '1h']):
    """
    Analyze simple strategies with fixed parameters
    """
    
    # Create reports directory
    reports_dir = 'reports'
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"{reports_dir}/simple_strategy_analysis_{symbol}_{timestamp}.md"
    
    # Initialize results storage
    all_results = []
    
    strategies = get_simple_strategies()
    
    print(f"🔍 ANALYZING {len(strategies)} SIMPLE STRATEGIES")
    print(f"🪙 SYMBOL: {symbol}")
    print(f"📅 PERIOD: {start_date} to {end_date}")
    print(f"💰 BALANCE: ${initial_balance:,}")
    print(f"🎯 REWARD RATIO: {reward_ratio}:1")
    print(f"🔄 REVERSE: {'Yes' if is_reverse else 'No'}")
    print(f"💰 FEES: {'Disabled' if no_fees else 'Enabled'}")
    print(f"📈 SCALING: {'Yes' if enable_scaling else 'No'} (x{scaling_multiplier})")
    print(f"⏰ TIMEFRAMES: {', '.join(timeframes)}")
    print("=" * 80)
    
    # Process each strategy
    for i, strategy in enumerate(strategies, 1):
        print(f"\n[{i}/{len(strategies)}] Testing: {strategy}")
        
        strategy_results = []
        
        for timeframe in timeframes:
            try:
                print(f"  ⏰ {timeframe}...", end=" ")
                
                # Run strategy
                result = run_strategy_with_timeframe(
                    strategy_name=strategy,
                    timeframe=timeframe,
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    initial_balance=initial_balance,
                    reward_ratio=reward_ratio,
                    is_reverse=is_reverse,
                    show_history_balance=False,
                    enable_scaling=enable_scaling,
                    scaling_threshold=1.0,
                    scaling_multiplier=scaling_multiplier,
                    no_fees=no_fees,
                    trailing_ratio=trailing_ratio
                )
                
                if result and 'metrics' in result:
                    metrics = result['metrics']
                    
                    # Extract key metrics
                    strategy_result = {
                        'strategy': strategy,
                        'timeframe': timeframe,
                        'total_trades': metrics.get('total_trades', 0),
                        'win_rate': metrics.get('win_rate', 0),
                        'total_return': metrics.get('total_return', 0),
                        'final_balance': metrics.get('final_balance', initial_balance),
                        'profit_factor': metrics.get('profit_factor', 0),
                        'max_drawdown': metrics.get('max_drawdown', 0),
                        'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                        'avg_trade': metrics.get('avg_trade', 0),
                        'avg_rr': metrics.get('avg_rr', 0),
                        'total_pnl': metrics.get('total_pnl', 0),
                        'winning_trades': metrics.get('winning_trades', 0),
                        'losing_trades': metrics.get('losing_trades', 0)
                    }
                    
                    strategy_results.append(strategy_result)
                    print(f"✅ {metrics.get('total_trades', 0)} trades, {metrics.get('win_rate', 0):.1f}% WR, {metrics.get('total_return', 0):.1f}% return")
                else:
                    print("❌ No result")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
        
        # Add best timeframe result for this strategy
        if strategy_results:
            # Sort by total return
            best_result = max(strategy_results, key=lambda x: x['total_return'])
            all_results.append(best_result)
    
    # Sort all results by total return
    all_results.sort(key=lambda x: x['total_return'], reverse=True)
    
    # Generate report
    generate_report(all_results, report_filename, symbol, start_date, end_date, 
                   initial_balance, reward_ratio, is_reverse, no_fees, 
                   enable_scaling, scaling_multiplier, timeframes)
    
    print(f"\n📊 REPORT GENERATED: {report_filename}")
    return all_results

def generate_report(results, filename, symbol, start_date, end_date, 
                   initial_balance, reward_ratio, is_reverse, no_fees,
                   enable_scaling, scaling_multiplier, timeframes):
    """Generate markdown report"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Simple Strategy Analysis Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Parameters section
        f.write("## 📋 Test Parameters\n\n")
        f.write(f"- **Symbol**: {symbol}\n")
        f.write(f"- **Period**: {start_date} to {end_date}\n")
        f.write(f"- **Initial Balance**: ${initial_balance:,}\n")
        f.write(f"- **Reward Ratio**: {reward_ratio}:1\n")
        f.write(f"- **Reverse Signal**: {'Yes' if is_reverse else 'No'}\n")
        f.write(f"- **Trading Fees**: {'Disabled' if no_fees else 'Enabled'}\n")
        f.write(f"- **Position Scaling**: {'Yes' if enable_scaling else 'No'}")
        if enable_scaling:
            f.write(f" (x{scaling_multiplier})")
        f.write("\n")
        f.write(f"- **Timeframes**: {', '.join(timeframes)}\n\n")
        
        # Summary statistics
        f.write("## 📊 Summary Statistics\n\n")
        if results:
            total_strategies = len(results)
            profitable_strategies = len([r for r in results if r['total_return'] > 0])
            avg_return = sum(r['total_return'] for r in results) / len(results)
            avg_win_rate = sum(r['win_rate'] for r in results) / len(results)
            
            f.write(f"- **Total Strategies Tested**: {total_strategies}\n")
            f.write(f"- **Profitable Strategies**: {profitable_strategies} ({profitable_strategies/total_strategies*100:.1f}%)\n")
            f.write(f"- **Average Return**: {avg_return:.1f}%\n")
            f.write(f"- **Average Win Rate**: {avg_win_rate:.1f}%\n\n")
        
        # Results table
        f.write("## 🏆 Strategy Rankings\n\n")
        f.write("| Rank | Strategy | Timeframe | Trades | Win Rate | Return | Final Balance | Profit Factor | Max DD | Sharpe |\n")
        f.write("|------|----------|-----------|--------|----------|--------|---------------|---------------|--------|--------|\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"| {i} | {result['strategy']} | {result['timeframe']} | {result['total_trades']} | {result['win_rate']:.1f}% | {result['total_return']:.1f}% | ${result['final_balance']:.0f} | {result['profit_factor']:.2f} | {result['max_drawdown']:.1f}% | {result['sharpe_ratio']:.2f} |\n")
        
        f.write("\n")
        
        # Top performers
        f.write("## 🥇 Top Performers\n\n")
        if results:
            top_5 = results[:5]
            for i, result in enumerate(top_5, 1):
                f.write(f"### {i}. {result['strategy']} ({result['timeframe']})\n")
                f.write(f"- **Return**: {result['total_return']:.1f}%\n")
                f.write(f"- **Win Rate**: {result['win_rate']:.1f}%\n")
                f.write(f"- **Trades**: {result['total_trades']}\n")
                f.write(f"- **Profit Factor**: {result['profit_factor']:.2f}\n")
                f.write(f"- **Max Drawdown**: {result['max_drawdown']:.1f}%\n\n")
        
        # Worst performers
        f.write("## 📉 Worst Performers\n\n")
        if results:
            worst_5 = results[-5:][::-1]  # Reverse to show worst first
            for i, result in enumerate(worst_5, 1):
                f.write(f"### {i}. {result['strategy']} ({result['timeframe']})\n")
                f.write(f"- **Return**: {result['total_return']:.1f}%\n")
                f.write(f"- **Win Rate**: {result['win_rate']:.1f}%\n")
                f.write(f"- **Trades**: {result['total_trades']}\n")
                f.write(f"- **Profit Factor**: {result['profit_factor']:.2f}\n")
                f.write(f"- **Max Drawdown**: {result['max_drawdown']:.1f}%\n\n")
        
        # Detailed results
        f.write("## 📈 Detailed Results\n\n")
        f.write("| Strategy | Timeframe | Trades | Win Rate | Return | Final Balance | Profit Factor | Max DD | Sharpe | Avg Trade | Avg R:R |\n")
        f.write("|----------|-----------|--------|----------|--------|---------------|---------------|--------|--------|-----------|---------|\n")
        
        for result in results:
            f.write(f"| {result['strategy']} | {result['timeframe']} | {result['total_trades']} | {result['win_rate']:.1f}% | {result['total_return']:.1f}% | ${result['final_balance']:.0f} | {result['profit_factor']:.2f} | {result['max_drawdown']:.1f}% | {result['sharpe_ratio']:.2f} | ${result['avg_trade']:.1f} | {result['avg_rr']:.1f} |\n")
        
        f.write("\n")
        f.write("---\n")
        f.write("*Generated by BTC Strategy Backtester*\n")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze simple strategies with fixed parameters')
    parser.add_argument('--symbol', default='SUIUSDT', help='Trading symbol')
    parser.add_argument('--start_date', default='2025-01-01', help='Start date')
    parser.add_argument('--end_date', default='2025-08-22', help='End date')
    parser.add_argument('--balance', type=int, default=1000, help='Initial balance')
    parser.add_argument('--reward_ratio', type=float, default=1.0, help='Reward ratio')
    parser.add_argument('--is_reverse', type=int, choices=[0, 1], default=1, help='Reverse signal')
    parser.add_argument('--no_fees', type=int, choices=[0, 1], default=1, help='Disable fees')
    parser.add_argument('--trailing_ratio', type=float, default=0, help='Trailing ratio')
    parser.add_argument('--enable_scaling', type=int, choices=[0, 1], default=1, help='Enable scaling')
    parser.add_argument('--scaling_multiplier', type=float, default=1.0, help='Scaling multiplier')
    
    args = parser.parse_args()
    
    # Run analysis
    results = analyze_simple_strategies(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_balance=args.balance,
        reward_ratio=args.reward_ratio,
        is_reverse=bool(args.is_reverse),
        no_fees=bool(args.no_fees),
        trailing_ratio=args.trailing_ratio,
        enable_scaling=bool(args.enable_scaling),
        scaling_multiplier=args.scaling_multiplier
    )
    
    print(f"\n✅ Analysis completed! Check the reports folder for detailed results.")
