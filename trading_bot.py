import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import uuid
import logging
from config import TradingConfig
from data_fetcher import DataFetcher
from strategies import TradingStrategies
from risk_manager import RiskManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

class TradingBot:
    def __init__(self, config=None):
        self.config = config or TradingConfig()
        self.data_fetcher = DataFetcher(self.config)
        self.strategies = TradingStrategies(self.config)
        self.risk_manager = RiskManager(self.config)
        
        self.active_trades = {}
        self.trade_history = []
        self.is_running = False
        
        logging.info("Trading Bot initialized")
    
    def start(self):
        """Start the trading bot"""
        self.is_running = True
        logging.info("Trading Bot started")
        
        while self.is_running:
            try:
                self._run_trading_cycle()
                time.sleep(30)  # Wait 30 seconds between cycles
                
            except KeyboardInterrupt:
                logging.info("Trading Bot stopped by user")
                self.stop()
                break
            except Exception as e:
                logging.error(f"Error in trading cycle: {e}")
                time.sleep(60)  # Wait longer on error
    
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        logging.info("Trading Bot stopped")
    
    def _run_trading_cycle(self):
        """Run one complete trading cycle"""
        logging.info("Starting trading cycle...")
        
        # Check if we should be trading
        if not self.risk_manager.is_trading_hours():
            logging.info("Outside trading hours, skipping cycle")
            return
        
        # Get market data
        market_data = self._get_market_data()
        if market_data.empty:
            logging.warning("No market data available")
            return
        
        # Check market conditions
        market_conditions = self.risk_manager.check_market_conditions(market_data)
        if not market_conditions['suitable']:
            logging.info(f"Market conditions not suitable: {market_conditions['reason']}")
            return
        
        # Check risk limits
        if not self.risk_manager.check_open_trades_limit():
            logging.info("Maximum open trades reached")
            return
        
        # Get trading signals
        signals = self.strategies.get_all_signals(market_data, '5m')
        best_signal = self.strategies.get_best_signal(market_data, '5m')
        
        # Log signals
        self._log_signals(signals, best_signal)
        
        # Execute trades if we have valid signals
        if best_signal['signal'] in ['long', 'short']:
            self._execute_trade(best_signal, market_data)
        
        # Check existing trades
        self._check_existing_trades(market_data)
        
        # Log summary
        self._log_summary()
    
    def _get_market_data(self):
        """Get market data for analysis"""
        try:
            # Get data for multiple timeframes
            data_5m = self.data_fetcher.get_ohlcv(self.config.SYMBOL, '5m', 100)
            data_1m = self.data_fetcher.get_ohlcv(self.config.SYMBOL, '1m', 50)
            
            # Use 5m data as primary, but add 1m data for scalping strategies
            if not data_5m.empty:
                return data_5m
            elif not data_1m.empty:
                return data_1m
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"Error getting market data: {e}")
            return pd.DataFrame()
    
    def _execute_trade(self, signal, market_data):
        """Execute a trade based on signal"""
        try:
            # Get account balance
            balance = self.data_fetcher.get_account_balance()
            if not balance or 'USDT' not in balance['free']:
                logging.error("Unable to get account balance")
                return
            
            usdt_balance = balance['free']['USDT']
            if usdt_balance < 10:  # Minimum balance check
                logging.warning("Insufficient USDT balance")
                return
            
            # Calculate position size
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            position_size = self.risk_manager.calculate_position_size(
                usdt_balance, entry_price, stop_loss
            )
            
            if position_size <= 0:
                logging.warning("Invalid position size calculated")
                return
            
            # Check daily risk limit
            risk_amount = abs(entry_price - stop_loss) * position_size
            if not self.risk_manager.check_daily_risk_limit(risk_amount):
                logging.warning("Daily risk limit would be exceeded")
                return
            
            # Create trade ID
            trade_id = str(uuid.uuid4())
            
            # Calculate trade details
            trade_info = {
                'id': trade_id,
                'symbol': self.config.SYMBOL,
                'side': signal['signal'],
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': signal['take_profit'],
                'position_size': position_size,
                'strategy': signal['strategy'],
                'confidence': signal['confidence'],
                'entry_time': datetime.now(),
                'status': 'open',
                'risk_amount': risk_amount
            }
            
            # Add to risk manager
            self.risk_manager.add_trade(trade_info)
            
            # Store in active trades
            self.active_trades[trade_id] = trade_info
            
            logging.info(f"Trade executed: {trade_info}")
            
            # In a real implementation, you would place the actual order here
            # self._place_order(trade_info)
            
        except Exception as e:
            logging.error(f"Error executing trade: {e}")
    
    def _check_existing_trades(self, market_data):
        """Check and manage existing trades"""
        current_price = market_data['close'].iloc[-1]
        
        for trade_id, trade in list(self.active_trades.items()):
            try:
                # Check stop loss
                if trade['side'] == 'long' and current_price <= trade['stop_loss']:
                    self._close_trade(trade_id, 'stop_loss', current_price)
                elif trade['side'] == 'short' and current_price >= trade['stop_loss']:
                    self._close_trade(trade_id, 'stop_loss', current_price)
                
                # Check take profit
                elif trade['side'] == 'long' and current_price >= trade['take_profit']:
                    self._close_trade(trade_id, 'take_profit', current_price)
                elif trade['side'] == 'short' and current_price <= trade['take_profit']:
                    self._close_trade(trade_id, 'take_profit', current_price)
                
            except Exception as e:
                logging.error(f"Error checking trade {trade_id}: {e}")
    
    def _close_trade(self, trade_id, reason, current_price):
        """Close a trade"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return
        
        # Calculate PnL
        if trade['side'] == 'long':
            pnl = (current_price - trade['entry_price']) * trade['position_size']
        else:
            pnl = (trade['entry_price'] - current_price) * trade['position_size']
        
        # Update trade info
        trade['exit_price'] = current_price
        trade['exit_time'] = datetime.now()
        trade['exit_reason'] = reason
        trade['pnl'] = pnl
        trade['status'] = 'closed'
        
        # Remove from active trades
        del self.active_trades[trade_id]
        
        # Update risk manager
        self.risk_manager.close_trade(trade_id, pnl)
        
        # Add to history
        self.trade_history.append(trade)
        
        logging.info(f"Trade closed: {trade}")
    
    def _log_signals(self, signals, best_signal):
        """Log trading signals"""
        logging.info("=== Trading Signals ===")
        for strategy, signal in signals.items():
            if signal['signal'] in ['long', 'short']:
                logging.info(f"{strategy}: {signal['signal'].upper()} - Confidence: {signal.get('confidence', 0):.2f}")
        
        if best_signal['signal'] in ['long', 'short']:
            logging.info(f"Best signal: {best_signal['strategy']} - {best_signal['signal'].upper()}")
        else:
            logging.info("No valid signals found")
    
    def _log_summary(self):
        """Log trading summary"""
        risk_summary = self.risk_manager.get_risk_summary()
        
        logging.info("=== Trading Summary ===")
        logging.info(f"Active trades: {risk_summary['open_trades_count']}")
        logging.info(f"Daily PnL: {risk_summary['daily_pnl']:.2f} USDT")
        logging.info(f"Daily risk used: {risk_summary['daily_risk_used']:.2f}%")
        logging.info(f"Trading hours: {risk_summary['trading_hours']}")
    
    def get_performance_summary(self):
        """Get performance summary"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'average_pnl': 0
            }
        
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t['pnl'] > 0])
        losing_trades = len([t for t in self.trade_history if t['pnl'] < 0])
        total_pnl = sum([t['pnl'] for t in self.trade_history])
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / total_trades) * 100 if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'average_pnl': total_pnl / total_trades if total_trades > 0 else 0
        }
    
    def backtest_strategy(self, start_date, end_date, initial_balance=10000):
        """
        Backtest the strategy on historical data
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_balance: Initial balance for backtest
        
        Returns:
            dict: Backtest results
        """
        logging.info(f"Starting backtest from {start_date} to {end_date}")
        
        # This is a simplified backtest - in a real implementation,
        # you would fetch historical data and run the strategies
        
        results = {
            'initial_balance': initial_balance,
            'final_balance': initial_balance,
            'total_return': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'trades': []
        }
        
        logging.info("Backtest completed")
        return results

def main():
    """Main function to run the trading bot"""
    try:
        # Create and start the trading bot
        bot = TradingBot()
        
        # Start the bot
        bot.start()
        
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
