#!/usr/bin/env python3
"""
Real-time Trading System Demo
Runs every 5 minutes using ultra_simple_strategy
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from backtest import Backtester
from config import TradingConfig

class RealTimeTrader:
    def __init__(self, symbol='SUIUSDT', initial_balance=1000, strategy_name='ultra_simple_strategy'):
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.strategy_name = strategy_name
        self.config = TradingConfig()
        
        # Initialize backtester
        self.backtester = Backtester(self.config)
        
        # Trading state
        self.current_balance = initial_balance
        self.savings_account = 0.0
        self.open_position = None
        self.trade_history = []
        self.equity_curve = []
        
        # Position scaling
        self.scaling_enabled = True
        self.scaling_threshold = 1.0
        self.scaling_multiplier = 2.0
        self.current_scaling_multiplier = 1.0
        
        # File paths
        self.data_dir = 'real_time_data'
        self.balance_file = f"{self.data_dir}/balance_{symbol}.json"
        self.trades_file = f"{self.data_dir}/trades_{symbol}.json"
        self.equity_file = f"{self.data_dir}/equity_{symbol}.json"
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{self.data_dir}/trading.log"),
                logging.StreamHandler()
            ]
        )
        
        # Load existing data
        self.load_trading_data()
        
    def load_trading_data(self):
        """Load existing trading data from files"""
        try:
            # Load balance
            if os.path.exists(self.balance_file):
                with open(self.balance_file, 'r') as f:
                    data = json.load(f)
                    self.current_balance = data.get('balance', self.initial_balance)
                    self.savings_account = data.get('savings_account', 0.0)
                    self.current_scaling_multiplier = data.get('scaling_multiplier', 1.0)
                    logging.info(f"Loaded balance: ${self.current_balance:.2f}, Savings: ${self.savings_account:.2f}")
            
            # Load trade history
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    self.trade_history = json.load(f)
                    logging.info(f"Loaded {len(self.trade_history)} historical trades")
            
            # Load equity curve
            if os.path.exists(self.equity_file):
                with open(self.equity_file, 'r') as f:
                    self.equity_curve = json.load(f)
                    logging.info(f"Loaded {len(self.equity_curve)} equity points")
                    
        except Exception as e:
            logging.error(f"Error loading trading data: {e}")
    
    def save_trading_data(self):
        """Save current trading data to files"""
        try:
            # Save balance
            balance_data = {
                'balance': self.current_balance,
                'savings_account': self.savings_account,
                'scaling_multiplier': self.current_scaling_multiplier,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.balance_file, 'w') as f:
                json.dump(balance_data, f, indent=2)
            
            # Save trade history
            with open(self.trades_file, 'w') as f:
                json.dump(self.trade_history, f, indent=2)
            
            # Save equity curve
            with open(self.equity_file, 'w') as f:
                json.dump(self.equity_curve, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving trading data: {e}")
    
    def get_current_market_data(self, timeframe='5m', limit=100):
        """Get current market data (demo version - will be replaced with real API)"""
        try:
            # For demo, we'll use historical data from a period we know has data
            end_date = datetime(2025, 8, 10, 12, 0, 0)  # Use known data period
            start_date = end_date - timedelta(hours=4)
            
            data = self.backtester._fetch_historical_data(
                self.symbol, start_date, end_date, timeframe
            )
            
            if data.empty:
                logging.error("No market data available")
                return None
            
            # Add indicators
            data = self.backtester._add_indicators(data)
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting market data: {e}")
            return None
    
    def check_position_exit(self, current_price):
        """Check if current position should be closed"""
        if not self.open_position:
            return None
        
        position = self.open_position
        exit_type = None
        exit_price = None
        
        # Check stop loss
        if position['side'] == 'long':
            if current_price <= position['stop_loss']:
                exit_type = 'stop_loss'
                exit_price = position['stop_loss']
            elif current_price >= position['take_profit']:
                exit_type = 'take_profit'
                exit_price = position['take_profit']
        else:  # short
            if current_price >= position['stop_loss']:
                exit_type = 'stop_loss'
                exit_price = position['stop_loss']
            elif current_price <= position['take_profit']:
                exit_type = 'take_profit'
                exit_price = position['take_profit']
        
        return exit_type, exit_price
    
    def close_position(self, exit_type, exit_price):
        """Close current position"""
        if not self.open_position:
            return
        
        position = self.open_position
        entry_price = position['entry_price']
        position_size = position['position_size']
        
        # Calculate PnL
        if position['side'] == 'long':
            pnl = (exit_price - entry_price) * position_size
        else:
            pnl = (entry_price - exit_price) * position_size
        
        # Apply trading fees (demo: 0.1%)
        fee = abs(position_size * exit_price * 0.001)
        pnl -= fee
        
        # Update balance
        self.current_balance += pnl
        
        # Apply savings logic
        if pnl > 0 and self.current_balance > self.initial_balance:
            profit_above_initial = self.current_balance - self.initial_balance
            save_amount = profit_above_initial * 0.10
            self.savings_account += save_amount
            self.current_balance -= save_amount
        
        # Record trade
        trade = {
            'entry_time': position['entry_time'],
            'exit_time': datetime.now().isoformat(),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'side': position['side'],
            'strategy': position['strategy'],
            'stop_loss': position['stop_loss'],
            'take_profit': position['take_profit'],
            'position_size': position_size,
            'exit_type': exit_type,
            'pnl': pnl,
            'fee': fee,
            'balance': self.current_balance,
            'savings_account': self.savings_account,
            'scaling_info': position.get('scaling_info', None)
        }
        
        self.trade_history.append(trade)
        
        # Update scaling multiplier
        if self.scaling_enabled:
            current_profit = self.current_balance - self.initial_balance
            current_rr = current_profit / (self.initial_balance * 0.01)
            
            if current_rr >= self.scaling_threshold:
                self.current_scaling_multiplier = self.scaling_multiplier
            else:
                self.current_scaling_multiplier = 1.0
        
        # Clear position
        self.open_position = None
        
        logging.info(f"Position closed: {exit_type} at ${exit_price:.4f}, PnL: ${pnl:.2f}, Balance: ${self.current_balance:.2f}")
        
        return trade
    
    def get_signal(self, data):
        """Get trading signal from strategy"""
        try:
            if data.empty or len(data) < 50:
                return None
            
            # Get latest data
            current_data = data.iloc[-50:]  # Last 50 candles
            
            # Get signal from strategy
            signal = self.backtester._get_signal(current_data, self.strategy_name, '5m')
            
            return signal
            
        except Exception as e:
            logging.error(f"Error getting signal: {e}")
            return None
    
    def open_new_position(self, signal, current_price):
        """Open new position based on signal"""
        if self.open_position:
            return None  # Already have position
        
        try:
            # Calculate position size (1R risk)
            risk_amount = self.initial_balance * 0.01  # 1% risk
            price_diff = abs(current_price - signal['stop_loss'])
            position_size = risk_amount / price_diff
            
            # Apply scaling
            if self.scaling_enabled:
                position_size *= self.current_scaling_multiplier
            
            # Calculate take profit (1:1 reward ratio)
            if signal['signal'] == 'long':
                take_profit = current_price + price_diff
            else:
                take_profit = current_price - price_diff
            
            # Create position
            position = {
                'side': signal['signal'],
                'entry_price': current_price,
                'entry_time': datetime.now().isoformat(),
                'strategy': signal['strategy'],
                'stop_loss': signal['stop_loss'],
                'take_profit': take_profit,
                'position_size': position_size,
                'scaling_info': {
                    'enabled': self.scaling_enabled,
                    'multiplier': self.current_scaling_multiplier
                }
            }
            
            self.open_position = position
            
            logging.info(f"New position opened: {signal['signal'].upper()} at ${current_price:.4f}, "
                        f"SL: ${signal['stop_loss']:.4f}, TP: ${take_profit:.4f}, "
                        f"Size: {position_size:.4f}, Scaling: {self.current_scaling_multiplier}x")
            
            return position
            
        except Exception as e:
            logging.error(f"Error opening position: {e}")
            return None
    
    def update_equity_curve(self):
        """Update equity curve with current balance"""
        equity_point = {
            'time': datetime.now().isoformat(),
            'balance': self.current_balance,
            'savings_account': self.savings_account,
            'total_wealth': self.current_balance + self.savings_account,
            'open_position': self.open_position is not None
        }
        
        self.equity_curve.append(equity_point)
        
        # Keep only last 1000 points
        if len(self.equity_curve) > 1000:
            self.equity_curve = self.equity_curve[-1000:]
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        try:
            logging.info(f"=== Trading Cycle Started at {datetime.now()} ===")
            
            # Get current market data
            data = self.get_current_market_data()
            if data is None or data.empty:
                logging.error("No market data available")
                return
            
            current_price = data.iloc[-1]['close']
            logging.info(f"Current {self.symbol} price: ${current_price:.4f}")
            
            # Check if we have an open position
            if self.open_position:
                # Check for exit
                exit_type, exit_price = self.check_position_exit(current_price)
                if exit_type:
                    self.close_position(exit_type, exit_price)
            
            # Look for new signal if no position
            if not self.open_position:
                signal = self.get_signal(data)
                if signal and signal['signal'] in ['long', 'short']:
                    self.open_new_position(signal, current_price)
            
            # Update equity curve
            self.update_equity_curve()
            
            # Save data
            self.save_trading_data()
            
            # Log summary
            total_wealth = self.current_balance + self.savings_account
            total_return = ((total_wealth - self.initial_balance) / self.initial_balance) * 100
            
            logging.info(f"Cycle Summary - Balance: ${self.current_balance:.2f}, "
                        f"Savings: ${self.savings_account:.2f}, "
                        f"Total Wealth: ${total_wealth:.2f}, "
                        f"Return: {total_return:.2f}%, "
                        f"Position: {'Open' if self.open_position else 'None'}")
            
            logging.info(f"=== Trading Cycle Completed ===")
            
        except Exception as e:
            logging.error(f"Error in trading cycle: {e}")
    
    def get_trading_summary(self):
        """Get trading summary"""
        total_wealth = self.current_balance + self.savings_account
        total_return = ((total_wealth - self.initial_balance) / self.initial_balance) * 100
        
        winning_trades = [t for t in self.trade_history if t['pnl'] > 0]
        losing_trades = [t for t in self.trade_history if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / len(self.trade_history) * 100 if self.trade_history else 0
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'savings_account': self.savings_account,
            'total_wealth': total_wealth,
            'total_return': total_return,
            'total_trades': len(self.trade_history),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'open_position': self.open_position is not None,
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Main function to run the trading system"""
    trader = RealTimeTrader(
        symbol='SUIUSDT',
        initial_balance=1000,
        strategy_name='ultra_simple_strategy'
    )
    
    # Run one trading cycle
    trader.run_trading_cycle()
    
    # Print summary
    summary = trader.get_trading_summary()
    print("\n" + "="*50)
    print("TRADING SUMMARY")
    print("="*50)
    print(f"Initial Balance: ${summary['initial_balance']:.2f}")
    print(f"Current Balance: ${summary['current_balance']:.2f}")
    print(f"Savings Account: ${summary['savings_account']:.2f}")
    print(f"Total Wealth: ${summary['total_wealth']:.2f}")
    print(f"Total Return: {summary['total_return']:.2f}%")
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Win Rate: {summary['win_rate']:.1f}%")
    print(f"Open Position: {'Yes' if summary['open_position'] else 'No'}")
    print("="*50)

if __name__ == "__main__":
    main()
