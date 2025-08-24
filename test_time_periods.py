#!/usr/bin/env python3
"""
Test ultra_simple_strategy with different time periods
From 2024-05-01 to 2025-08-20
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from run_strategy_timeframe import run_strategy_with_timeframe

def create_time_periods():
    """Create different time periods for testing"""
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2025, 8, 20)
    
    periods = []
    
    # 2 weeks periods
    current = start_date
    while current + timedelta(days=14) <= end_date:
        period_end = current + timedelta(days=14)
        periods.append({
            'name': '2 weeks',
            'start': current.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d'),
            'days': 14
        })
        current = period_end
    
    # 1 month periods
    current = start_date
    while current + timedelta(days=30) <= end_date:
        period_end = current + timedelta(days=30)
        periods.append({
            'name': '1 month',
            'start': current.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d'),
            'days': 30
        })
        current = period_end
    
    # 2 months periods
    current = start_date
    while current + timedelta(days=60) <= end_date:
        period_end = current + timedelta(days=60)
        periods.append({
            'name': '2 months',
            'start': current.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d'),
            'days': 60
        })
        current = period_end
    
    # 3 months periods
    current = start_date
    while current + timedelta(days=90) <= end_date:
        period_end = current + timedelta(days=90)
        periods.append({
            'name': '3 months',
            'start': current.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d'),
            'days': 90
        })
        current = period_end
    
    # 6 months periods
    current = start_date
    while current + timedelta(days=180) <= end_date:
        period_end = current + timedelta(days=180)
        periods.append({
            'name': '6 months',
            'start': current.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d'),
            'days': 180
        })
        current = period_end
    
    # 1 year periods
    current = start_date
    while current + timedelta(days=365) <= end_date:
        period_end = current + timedelta(days=365)
        periods.append({
            'name': '1 year',
            'start': current.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d'),
            'days': 365
        })
        current = period_end
    
    # Full period
    periods.append({
        'name': 'Full period',
        'start': start_date.strftime('%Y-%m-%d'),
        'end': end_date.strftime('%Y-%m-%d'),
        'days': (end_date - start_date).days
    })
    
    return periods

def test_time_periods():
    """Test strategy with different time periods"""
    
    # Create reports directory
    reports_dir = 'reports'
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"{reports_dir}/time_period_analysis_{timestamp}.md"
    
    # Get time periods
    periods = create_time_periods()
    
    print(f"🔍 TESTING ULTRA_SIMPLE_STRATEGY WITH DIFFERENT TIME PERIODS")
    print(f"🪙 SYMBOL: SUIUSDT")
    print(f"⏰ TIMEFRAME: 5m")
    print(f"💰 BALANCE: $100")
    print(f"🎯 REWARD RATIO: 1:1")
    print(f"🔄 REVERSE: Yes")
    print(f"💰 FEES: Disabled")
    print(f"📈 SCALING: Yes (x2)")
    print(f"📅 TOTAL PERIODS: {len(periods)}")
    print("=" * 80)
    
    # Initialize results storage
    all_results = []
    
    # Test each period
    for i, period in enumerate(periods, 1):
        print(f"\n[{i}/{len(periods)}] Testing: {period['name']} ({period['start']} to {period['end']})")
        
        try:
            # Run strategy
            result = run_strategy_with_timeframe(
                strategy_name='ultra_simple_strategy',
                timeframe='5m',
                symbol='SUIUSDT',
                start_date=period['start'],
                end_date=period['end'],
                initial_balance=100,
                reward_ratio=1.0,
                is_reverse=True,
                show_history_balance=False,
                enable_scaling=True,
                scaling_threshold=1.0,
                scaling_multiplier=2.0,
                no_fees=True,
                trailing_ratio=0
            )
            
            if result and 'metrics' in result:
                metrics = result['metrics']
                
                # Extract key metrics
                period_result = {
                    'period_name': period['name'],
                    'start_date': period['start'],
                    'end_date': period['end'],
                    'days': period['days'],
                    'total_trades': metrics.get('total_trades', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'total_return': metrics.get('total_return', 0),
                    'final_balance': metrics.get('final_balance', 100),
                    'savings_account': result.get('savings_account', 0),
                    'total_wealth': result.get('total_wealth', 100),
                    'profit_factor': metrics.get('profit_factor', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'avg_trade': metrics.get('avg_trade', 0),
                    'avg_rr': metrics.get('avg_rr', 0),
                    'total_pnl': metrics.get('total_pnl', 0),
                    'winning_trades': metrics.get('winning_trades', 0),
                    'losing_trades': metrics.get('losing_trades', 0),
                    'account_blown': result.get('account_blown', False)
                }
                
                all_results.append(period_result)
                
                # Print summary
                if period_result['account_blown']:
                    print(f"  ❌ ACCOUNT BLOWN! {period_result['total_trades']} trades")
                else:
                    print(f"  ✅ {period_result['total_trades']} trades, {period_result['win_rate']:.1f}% WR, {period_result['total_return']:.1f}% return")
                    print(f"     💰 Balance: ${period_result['final_balance']:.2f}, Savings: ${period_result['savings_account']:.2f}")
            else:
                print(f"  ❌ No result")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            continue
    
    # Sort results by total return
    all_results.sort(key=lambda x: x['total_return'], reverse=True)
    
    # Generate report
    generate_report(all_results, report_filename)
    
    print(f"\n📊 REPORT GENERATED: {report_filename}")
    return all_results

def generate_report(results, filename):
    """Generate markdown report"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Time Period Analysis Report - ultra_simple_strategy\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Parameters section
        f.write("## 📋 Test Parameters\n\n")
        f.write(f"- **Strategy**: ultra_simple_strategy\n")
        f.write(f"- **Symbol**: SUIUSDT\n")
        f.write(f"- **Timeframe**: 5m\n")
        f.write(f"- **Initial Balance**: $100\n")
        f.write(f"- **Reward Ratio**: 1:1\n")
        f.write(f"- **Reverse Signal**: Yes\n")
        f.write(f"- **Trading Fees**: Disabled\n")
        f.write(f"- **Position Scaling**: Yes (x2)\n")
        f.write(f"- **Test Period**: 2024-05-01 to 2025-08-20\n\n")
        
        # Summary statistics
        f.write("## 📊 Summary Statistics\n\n")
        if results:
            total_periods = len(results)
            profitable_periods = len([r for r in results if r['total_return'] > 0])
            blown_accounts = len([r for r in results if r['account_blown']])
            avg_return = sum(r['total_return'] for r in results) / len(results)
            avg_win_rate = sum(r['win_rate'] for r in results) / len(results)
            
            f.write(f"- **Total Periods Tested**: {total_periods}\n")
            f.write(f"- **Profitable Periods**: {profitable_periods} ({profitable_periods/total_periods*100:.1f}%)\n")
            f.write(f"- **Blown Accounts**: {blown_accounts} ({blown_accounts/total_periods*100:.1f}%)\n")
            f.write(f"- **Average Return**: {avg_return:.1f}%\n")
            f.write(f"- **Average Win Rate**: {avg_win_rate:.1f}%\n\n")
        
        # Top performers by period type
        f.write("## 🏆 Best Performers by Period Type\n\n")
        
        # Group by period type
        period_types = {}
        for result in results:
            period_name = result['period_name']
            if period_name not in period_types:
                period_types[period_name] = []
            period_types[period_name].append(result)
        
        for period_name, period_results in period_types.items():
            if period_results:
                best_result = max(period_results, key=lambda x: x['total_return'])
                f.write(f"### {period_name}\n")
                f.write(f"- **Best Period**: {best_result['start_date']} to {best_result['end_date']}\n")
                f.write(f"- **Return**: {best_result['total_return']:.1f}%\n")
                f.write(f"- **Trades**: {best_result['total_trades']}\n")
                f.write(f"- **Win Rate**: {best_result['win_rate']:.1f}%\n")
                f.write(f"- **Final Balance**: ${best_result['final_balance']:.2f}\n")
                f.write(f"- **Savings**: ${best_result['savings_account']:.2f}\n")
                f.write(f"- **Total Wealth**: ${best_result['total_wealth']:.2f}\n\n")
        
        # Results table
        f.write("## 📈 All Results (Ranked by Return)\n\n")
        f.write("| Rank | Period | Start | End | Days | Trades | Win Rate | Return | Balance | Savings | Total Wealth | Max DD |\n")
        f.write("|------|--------|-------|-----|------|--------|----------|--------|---------|---------|--------------|--------|\n")
        
        for i, result in enumerate(results, 1):
            blown_marker = "🔥" if result['account_blown'] else ""
            f.write(f"| {i} | {result['period_name']} | {result['start_date']} | {result['end_date']} | {result['days']} | {result['total_trades']} | {result['win_rate']:.1f}% | {result['total_return']:.1f}% | ${result['final_balance']:.2f} | ${result['savings_account']:.2f} | ${result['total_wealth']:.2f} | {result['max_drawdown']:.1f}% | {blown_marker}\n")
        
        f.write("\n")
        
        # Top 10 performers
        f.write("## 🥇 Top 10 Performers\n\n")
        if results:
            top_10 = results[:10]
            for i, result in enumerate(top_10, 1):
                f.write(f"### {i}. {result['period_name']} ({result['start_date']} to {result['end_date']})\n")
                f.write(f"- **Return**: {result['total_return']:.1f}%\n")
                f.write(f"- **Trades**: {result['total_trades']}\n")
                f.write(f"- **Win Rate**: {result['win_rate']:.1f}%\n")
                f.write(f"- **Final Balance**: ${result['final_balance']:.2f}\n")
                f.write(f"- **Savings**: ${result['savings_account']:.2f}\n")
                f.write(f"- **Total Wealth**: ${result['total_wealth']:.2f}\n")
                f.write(f"- **Max Drawdown**: {result['max_drawdown']:.1f}%\n\n")
        
        # Worst performers
        f.write("## 📉 Worst Performers\n\n")
        if results:
            worst_10 = results[-10:][::-1]  # Reverse to show worst first
            for i, result in enumerate(worst_10, 1):
                blown_marker = "🔥 BLOWN" if result['account_blown'] else ""
                f.write(f"### {i}. {result['period_name']} ({result['start_date']} to {result['end_date']}) {blown_marker}\n")
                f.write(f"- **Return**: {result['total_return']:.1f}%\n")
                f.write(f"- **Trades**: {result['total_trades']}\n")
                f.write(f"- **Win Rate**: {result['win_rate']:.1f}%\n")
                f.write(f"- **Final Balance**: ${result['final_balance']:.2f}\n")
                f.write(f"- **Max Drawdown**: {result['max_drawdown']:.1f}%\n\n")
        
        # Period type analysis
        f.write("## 📊 Period Type Analysis\n\n")
        f.write("| Period Type | Count | Avg Return | Best Return | Worst Return | Success Rate |\n")
        f.write("|-------------|-------|------------|-------------|--------------|--------------|\n")
        
        for period_name, period_results in period_types.items():
            if period_results:
                avg_return = sum(r['total_return'] for r in period_results) / len(period_results)
                best_return = max(r['total_return'] for r in period_results)
                worst_return = min(r['total_return'] for r in period_results)
                success_rate = len([r for r in period_results if r['total_return'] > 0]) / len(period_results) * 100
                
                f.write(f"| {period_name} | {len(period_results)} | {avg_return:.1f}% | {best_return:.1f}% | {worst_return:.1f}% | {success_rate:.1f}% |\n")
        
        f.write("\n")
        f.write("---\n")
        f.write("*Generated by BTC Strategy Backtester*\n")

if __name__ == "__main__":
    # Run analysis
    results = test_time_periods()
    
    print(f"\n✅ Time period analysis completed!")
    print(f"📊 Check the reports folder for detailed results.")
