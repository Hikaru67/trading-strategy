import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
import logging
from config import TradingConfig
from strategies import TradingStrategies
from indicators import TechnicalIndicators

class Backtester:
    def __init__(self, config=None):
        self.config = config or TradingConfig()
        self.strategies = TradingStrategies(self.config)
        self.indicators = TechnicalIndicators()
        
        # Initialize exchange for historical data
        self.exchange = ccxt.binance({
            'enableRateLimit': True
        })
        
        self.results = {
            'trades': [],
            'equity_curve': [],
            'metrics': {}
        }
    
    def run_backtest(self, symbol, start_date, end_date, initial_balance=10000, strategy_name='all'):
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading symbol
            start_date: Start date (datetime)
            end_date: End date (datetime)
            initial_balance: Initial balance
            strategy_name: Strategy to test ('all' for all strategies)
        
        Returns:
            dict: Backtest results
        """
        logging.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
        
        # Fetch historical data
        data = self._fetch_historical_data(symbol, start_date, end_date)
        if data.empty:
            logging.error("No historical data available")
            return None
        
        # Initialize backtest variables
        balance = initial_balance
        position = None
        trades = []
        equity_curve = []
        
        # Add indicators to data
        data = self._add_indicators(data)
        
        # Run backtest
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']
            current_time = data.index[i]
            
            # Skip if not enough data for indicators
            if len(current_data) < 50:
                continue
            
            # Check if we have an open position
            if position is not None:
                # Check stop loss and take profit
                if self._should_close_position(position, current_price, current_data):
                    # Close position
                    pnl = self._calculate_pnl(position, current_price)
                    balance += pnl
                    
                    # Record trade
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'side': position['side'],
                        'strategy': position['strategy'],
                        'pnl': pnl,
                        'balance': balance
                    }
                    trades.append(trade)
                    
                    position = None
            
            # Look for new signals if no position
            if position is None:
                signal = self._get_signal(current_data, strategy_name)
                
                if signal['signal'] in ['long', 'short']:
                    # Calculate position size
                    position_size = self._calculate_position_size(balance, signal)
                    
                    if position_size > 0:
                        position = {
                            'side': signal['signal'],
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'strategy': signal['strategy'],
                            'stop_loss': signal['stop_loss'],
                            'take_profit': signal['take_profit'],
                            'position_size': position_size
                        }
            
            # Record equity
            equity_curve.append({
                'time': current_time,
                'balance': balance,
                'position_value': self._get_position_value(position, current_price) if position else 0
            })
        
        # Close any remaining position
        if position is not None:
            final_price = data.iloc[-1]['close']
            pnl = self._calculate_pnl(position, final_price)
            balance += pnl
            
            trade = {
                'entry_time': position['entry_time'],
                'exit_time': data.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'side': position['side'],
                'strategy': position['strategy'],
                'pnl': pnl,
                'balance': balance
            }
            trades.append(trade)
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades, initial_balance, equity_curve)
        
        self.results = {
            'trades': trades,
            'equity_curve': equity_curve,
            'metrics': metrics,
            'final_balance': balance,
            'total_return': ((balance - initial_balance) / initial_balance) * 100
        }
        
        logging.info(f"Backtest completed. Final balance: {balance:.2f}, Return: {self.results['total_return']:.2f}%")
        
        return self.results
    
    def _fetch_historical_data(self, symbol, start_date, end_date):
        """Fetch historical OHLCV data"""
        try:
            # Convert dates to timestamps
            start_timestamp = int(start_date.timestamp() * 1000)
            end_timestamp = int(end_date.timestamp() * 1000)
            
            # Fetch data in chunks
            all_data = []
            current_timestamp = start_timestamp
            
            while current_timestamp < end_timestamp:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, 
                    '5m', 
                    since=current_timestamp, 
                    limit=1000
                )
                
                if not ohlcv:
                    break
                
                all_data.extend(ohlcv)
                current_timestamp = ohlcv[-1][0] + 1
            
            # Convert to DataFrame
            if all_data:
                df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Filter by date range
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def _add_indicators(self, data):
        """Add technical indicators to data"""
        if data.empty:
            return data
        
        # Calculate all indicators
        data['atr'] = self.indicators.calculate_atr(data['high'], data['low'], data['close'])
        data['ema_20'] = self.indicators.calculate_ema(data['close'], 20)
        data['ema_50'] = self.indicators.calculate_ema(data['close'], 50)
        data['rsi'] = self.indicators.calculate_rsi(data['close'])
        
        bb = self.indicators.calculate_bollinger_bands(data['close'])
        data['bb_upper'] = bb['upper']
        data['bb_middle'] = bb['middle']
        data['bb_lower'] = bb['lower']
        
        stoch = self.indicators.calculate_stochastic(data['high'], data['low'], data['close'])
        data['stoch_k'] = stoch['k']
        data['stoch_d'] = stoch['d']
        
        macd = self.indicators.calculate_macd(data['close'])
        data['macd'] = macd['macd']
        data['macd_signal'] = macd['signal']
        data['macd_histogram'] = macd['histogram']
        
        data['vwap'] = self.indicators.calculate_vwap(data['high'], data['low'], data['close'], data['volume'])
        
        ichimoku = self.indicators.calculate_ichimoku(data['high'], data['low'], data['close'])
        data['tenkan_sen'] = ichimoku['tenkan_sen']
        data['kijun_sen'] = ichimoku['kijun_sen']
        data['senkou_span_a'] = ichimoku['senkou_span_a']
        data['senkou_span_b'] = ichimoku['senkou_span_b']
        data['chikou_span'] = ichimoku['chikou_span']
        
        data['obv'] = self.indicators.calculate_obv(data['close'], data['volume'])
        
        vsa_signals = self.indicators.calculate_vsa_signals(
            data['open'], data['high'], data['low'], data['close'], data['volume']
        )
        data = pd.concat([data, vsa_signals], axis=1)
        
        return data
    
    def _get_signal(self, data, strategy_name):
        """Get trading signal from specified strategy"""
        if strategy_name == 'all':
            return self.strategies.get_best_signal(data, '1h')
        elif strategy_name == 'ema_rsi':
            return self.strategies.ema_rsi_strategy(data, '1h')
        elif strategy_name == 'bollinger_stochastic':
            return self.strategies.bollinger_stochastic_strategy(data, '1h')
        elif strategy_name == 'macd_vwap':
            return self.strategies.macd_vwap_strategy(data, '1h')
        elif strategy_name == 'ichimoku':
            return self.strategies.ichimoku_strategy(data, '1h')
        elif strategy_name == 'vsa_obv':
            return self.strategies.vsa_obv_strategy(data, '1h')
        elif strategy_name == 'multi_indicator':
            return self.strategies.multi_indicator_strategy(data, '1h')
        else:
            return {'signal': 'no_signal', 'reason': 'Invalid strategy'}
    
    def _calculate_position_size(self, balance, signal):
        """Calculate position size based on risk management"""
        risk_percentage = self.config.MAX_RISK_PER_TRADE
        risk_amount = balance * risk_percentage
        
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0
        
        position_size = risk_amount / price_diff
        
        # Apply position size limits
        max_position_value = balance * self.config.MAX_POSITION_SIZE
        max_position_size = max_position_value / entry_price
        
        return min(position_size, max_position_size)
    
    def _should_close_position(self, position, current_price, current_data):
        """Check if position should be closed"""
        if position['side'] == 'long':
            # Check stop loss
            if current_price <= position['stop_loss']:
                return True
            # Check take profit
            if current_price >= position['take_profit']:
                return True
        else:  # short
            # Check stop loss
            if current_price >= position['stop_loss']:
                return True
            # Check take profit
            if current_price <= position['take_profit']:
                return True
        
        return False
    
    def _calculate_pnl(self, position, current_price):
        """Calculate PnL for a position"""
        if position['side'] == 'long':
            return (current_price - position['entry_price']) * position['position_size']
        else:
            return (position['entry_price'] - current_price) * position['position_size']
    
    def _get_position_value(self, position, current_price):
        """Get current value of position"""
        if position is None:
            return 0
        return position['position_size'] * current_price
    
    def _calculate_metrics(self, trades, initial_balance, equity_curve):
        """Calculate performance metrics"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'average_pnl': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'profit_factor': 0
            }
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        
        total_pnl = sum([t['pnl'] for t in trades])
        average_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = sum([t['pnl'] for t in winning_trades])
        gross_loss = abs(sum([t['pnl'] for t in losing_trades]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Maximum drawdown
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # Sharpe ratio (simplified)
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i-1]['balance'] + equity_curve[i-1]['position_value']
            curr_equity = equity_curve[i]['balance'] + equity_curve[i]['position_value']
            returns.append((curr_equity - prev_equity) / prev_equity)
        
        sharpe_ratio = 0
        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'average_pnl': average_pnl,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': profit_factor
        }
    
    def _calculate_max_drawdown(self, equity_curve):
        """Calculate maximum drawdown"""
        if not equity_curve:
            return 0
        
        peak = equity_curve[0]['balance'] + equity_curve[0]['position_value']
        max_dd = 0
        
        for point in equity_curve:
            equity = point['balance'] + point['position_value']
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd * 100  # Return as percentage
    
    def print_results(self):
        """Print backtest results"""
        if not self.results:
            print("No backtest results available")
            return
        
        metrics = self.results['metrics']
        trades = self.results['trades']
        
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']}")
        print(f"Losing Trades: {metrics['losing_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Total PnL: {metrics['total_pnl']:.2f} USDT")
        print(f"Average PnL: {metrics['average_pnl']:.2f} USDT")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Total Return: {self.results['total_return']:.2f}%")
        print("="*50)
        
        # Print recent trades
        if trades:
            print("\nRecent Trades:")
            print("-" * 80)
            print(f"{'Entry Time':<20} {'Exit Time':<20} {'Side':<6} {'Strategy':<15} {'PnL':<10}")
            print("-" * 80)
            
            for trade in trades[-10:]:  # Show last 10 trades
                print(f"{trade['entry_time']:<20} {trade['exit_time']:<20} {trade['side']:<6} {trade['strategy']:<15} {trade['pnl']:<10.2f}")

def main():
    """Main function to run backtest"""
    # Create backtester
    backtester = Backtester()
    
    # Define backtest parameters
    symbol = 'BTCUSDT'
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    initial_balance = 10000
    
    # Run backtest
    results = backtester.run_backtest(symbol, start_date, end_date, initial_balance, 'all')
    
    if results:
        backtester.print_results()
    else:
        print("Backtest failed")

if __name__ == "__main__":
    main()
