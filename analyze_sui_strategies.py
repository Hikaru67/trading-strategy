#!/usr/bin/env python3
"""
Analyze all strategies for SUIUSDT
"""

import pandas as pd
from datetime import datetime
from backtest import Backtester
import os

def analyze_sui_strategies(no_fees=False):
    """Analyze all strategies for SUIUSDT"""
    print("🔍 ANALYZING SUIUSDT STRATEGIES")
    print("=" * 60)
    
    # Parameters
    symbol = 'SUIUSDT'
    start_date = datetime(2025, 8, 1)
    end_date = datetime(2025, 8, 22)
    balance = 1000
    timeframe = '5m'
    
    print(f"🪙 Symbol: {symbol}")
    print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"💰 Balance: ${balance:,}")
    print(f"⏰ Timeframe: {timeframe}")
    print(f"💰 Trading Fees: {'DISABLED' if no_fees else 'ENABLED'}")
    print("=" * 60)
    
    # List of strategies to test
    strategies = [
        'ema_rsi',
        'ultra_simple_strategy',
        'bollinger_stochastic',
        'macd_vwap',
        'ichimoku',
        'vsa_obv',
        'multi_indicator',
        'ema_rsi_ichimoku',
        'enhanced_with_candlestick',
        'divergence_strategy',
        'simple_divergence_strategy',
        'wyckoff_vsa',
        'practical_wyckoff_vsa',
        'smart_tp_strategy',
        'adaptive_tp_strategy',
        'smc_strategy',
        'breaker_block_strategy'
    ]
    
    # Results storage
    results = []
    
    # Create backtester
    backtester = Backtester()
    
    for i, strategy in enumerate(strategies, 1):
        print(f"\n[{i:2d}/{len(strategies)}] Testing: {strategy}")
        print("-" * 40)
        
        try:
            # Run backtest
            result = backtester.run_backtest(
                symbol=symbol,
                strategy_name=strategy,
                start_date=start_date,
                end_date=end_date,
                initial_balance=balance,
                timeframe=timeframe,
                no_fees=no_fees
            )
            
            if result:
                metrics = result.get('metrics', {})
                trades = result.get('trades', [])
                
                # Extract key metrics
                total_trades = metrics.get('total_trades', 0)
                win_rate = metrics.get('win_rate', 0)
                total_return = result.get('total_return', 0)
                final_balance = result.get('final_balance', balance)
                profit_factor = metrics.get('profit_factor', 0)
                max_drawdown = metrics.get('max_drawdown', 0)
                
                # Calculate average trade
                avg_trade = 0
                if total_trades > 0:
                    total_pnl = sum([t['pnl'] for t in trades])
                    avg_trade = total_pnl / total_trades
                
                # Store results
                results.append({
                    'strategy': strategy,
                    'total_trades': total_trades,
                    'win_rate': win_rate,
                    'total_return': total_return,
                    'final_balance': final_balance,
                    'profit_factor': profit_factor,
                    'max_drawdown': max_drawdown,
                    'avg_trade': avg_trade,
                    'status': 'Success'
                })
                
                print(f"  ✅ Trades: {total_trades}")
                print(f"  📊 Win Rate: {win_rate:.1f}%")
                print(f"  💰 Return: {total_return:.2f}%")
                print(f"  📈 Final Balance: ${final_balance:.2f}")
                print(f"  📊 Profit Factor: {profit_factor:.2f}")
                print(f"  📉 Max DD: {max_drawdown:.2f}%")
                print(f"  💵 Avg Trade: ${avg_trade:.2f}")
                
            else:
                results.append({
                    'strategy': strategy,
                    'total_trades': 0,
                    'win_rate': 0,
                    'total_return': 0,
                    'final_balance': balance,
                    'profit_factor': 0,
                    'max_drawdown': 0,
                    'avg_trade': 0,
                    'status': 'No signals'
                })
                print(f"  ⚠️  No signals generated")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({
                'strategy': strategy,
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'final_balance': balance,
                'profit_factor': 0,
                'max_drawdown': 0,
                'avg_trade': 0,
                'status': f'Error: {str(e)}'
            })
    
    # Create summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY REPORT")
    print("=" * 60)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(results)
    
    # Filter successful strategies
    successful = df[df['status'] == 'Success']
    
    if len(successful) > 0:
        print(f"\n✅ Successful Strategies: {len(successful)}/{len(strategies)}")
        
        # Sort by different metrics
        print(f"\n🏆 TOP 5 BY TOTAL TRADES:")
        top_trades = successful.nlargest(5, 'total_trades')[['strategy', 'total_trades', 'win_rate', 'total_return']]
        print(top_trades.to_string(index=False))
        
        print(f"\n💰 TOP 5 BY RETURN:")
        top_return = successful.nlargest(5, 'total_return')[['strategy', 'total_return', 'total_trades', 'win_rate']]
        print(top_return.to_string(index=False))
        
        print(f"\n🎯 TOP 5 BY WIN RATE:")
        top_winrate = successful.nlargest(5, 'win_rate')[['strategy', 'win_rate', 'total_trades', 'total_return']]
        print(top_winrate.to_string(index=False))
        
        print(f"\n📊 TOP 5 BY PROFIT FACTOR:")
        top_pf = successful.nlargest(5, 'profit_factor')[['strategy', 'profit_factor', 'total_trades', 'total_return']]
        print(top_pf.to_string(index=False))
        
        # Statistics
        print(f"\n📈 STATISTICS:")
        print(f"  Average Trades: {successful['total_trades'].mean():.1f}")
        print(f"  Average Win Rate: {successful['win_rate'].mean():.1f}%")
        print(f"  Average Return: {successful['total_return'].mean():.2f}%")
        print(f"  Average Profit Factor: {successful['profit_factor'].mean():.2f}")
        print(f"  Average Max DD: {successful['max_drawdown'].mean():.2f}%")
        
        # Profitable strategies
        profitable = successful[successful['total_return'] > 0]
        print(f"\n💚 Profitable Strategies: {len(profitable)}/{len(successful)}")
        if len(profitable) > 0:
            print(profitable[['strategy', 'total_return', 'total_trades', 'win_rate']].to_string(index=False))
    
    # Failed strategies
    failed = df[df['status'] != 'Success']
    if len(failed) > 0:
        print(f"\n❌ Failed Strategies: {len(failed)}")
        print(failed[['strategy', 'status']].to_string(index=False))
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sui_strategy_analysis_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Detailed results saved to: {filename}")
    
    return df

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze all strategies for SUIUSDT')
    parser.add_argument('--no_fees', type=int, choices=[0, 1], default=0, help='Disable trading fees (0=normal fees, 1=no fees)')
    
    args = parser.parse_args()
    analyze_sui_strategies(no_fees=args.no_fees)
