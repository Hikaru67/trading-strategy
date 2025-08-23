import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
import logging
from config import TradingConfig
from strategies import TradingStrategies
from indicators import TechnicalIndicators
from utils import get_cached_fetcher

class Backtester:
    def __init__(self, config=None):
        self.config = config or TradingConfig()
        self.strategies = TradingStrategies(self.config)
        self.indicators = TechnicalIndicators()
        
        # Initialize exchange for historical data
        self.exchange = ccxt.binance({
            'enableRateLimit': True
        })
        
        # Initialize cached data fetcher
        from utils import DataFetcher
        self.data_fetcher = DataFetcher(self.exchange)
        self.cached_fetcher = get_cached_fetcher(self.data_fetcher)
        
        self.results = {
            'trades': [],
            'equity_curve': [],
            'metrics': {}
        }
    
    def run_backtest(self, symbol, start_date, end_date, initial_balance=10000, strategy_name='all', timeframe='1h', enable_scaling=False, scaling_threshold=1.0, scaling_multiplier=2.0):
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading symbol
            start_date: Start date (datetime)
            end_date: End date (datetime)
            initial_balance: Initial balance
            strategy_name: Strategy to test ('all' for all strategies)
            timeframe: Timeframe to use ('5m', '15m', '30m', '1h', '2h', '4h')
        
        Returns:
            dict: Backtest results
        """
        logging.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
        
        # Fetch historical data
        data = self._fetch_historical_data(symbol, start_date, end_date, timeframe)
        if data.empty:
            logging.error("No historical data available")
            return None
        
        # Initialize backtest variables
        balance = initial_balance
        position = None
        trades = []
        equity_curve = []
        
        # Position scaling variables
        scaling_enabled = enable_scaling
        scaling_threshold_rr = scaling_threshold
        scaling_risk_multiplier = scaling_multiplier
        current_scaling_multiplier = 1.0  # Start with normal risk
        
        # Initialize exit counters
        exit_counters = {
            'stop_loss': 0,
            'stop_loss_at_entry': 0,  # Trailing stop moved to entry
            'take_profit': 0
        }
        
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
                exit_type = self._should_close_position(position, current_price, current_data)
                

                
                if exit_type:
                    # Calculate exact exit price based on exit type
                    if exit_type == 'stop_loss':
                        exit_price = position['stop_loss']
                    elif exit_type == 'take_profit':
                        exit_price = position['take_profit']
                    elif exit_type == 'stop_loss_at_entry':
                        exit_price = position['entry_price']
                    else:
                        exit_price = current_price  # fallback
                    
                    # Close position with exact exit price
                    pnl = self._calculate_pnl(position, exit_price)
                    balance += pnl
                    
                    # Check if account is blown (balance <= 0)
                    if balance <= 0:
                        # Record trade before stopping
                        trade = {
                            'entry_time': position['entry_time'],
                            'exit_time': current_time,
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'side': position['side'],
                            'strategy': position['strategy'],
                            'stop_loss': position['stop_loss'],
                            'take_profit': position['take_profit'],
                            'position_size': position['position_size'],
                            'exit_type': exit_type,
                            'pnl': pnl,
                            'balance': balance,
                            'scaling_info': position.get('scaling_info', None)
                        }
                        trades.append(trade)
                        
                        # Update exit counters
                        exit_counters[exit_type] += 1
                        
                        # Stop trading - account blown
                        logging.warning(f"🔥 ACCOUNT BLOWN! Balance: ${balance:.2f} at {current_time}")
                        print(f"\n🔥 ACCOUNT BLOWN! Balance: ${balance:.2f}")
                        print(f"📅 Blown at: {current_time}")
                        print(f"💸 Final PnL: ${pnl:.2f}")
                        print(f"📊 Total trades before blow: {len(trades)}")
                        
                        # Break out of main loop
                        break
                    
                    # Update exit counters
                    exit_counters[exit_type] += 1
                    
                    # Record trade
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'side': position['side'],
                        'strategy': position['strategy'],
                        'stop_loss': position['stop_loss'],
                        'take_profit': position['take_profit'],
                        'position_size': position['position_size'],
                        'exit_type': exit_type,
                        'pnl': pnl,
                        'balance': balance,
                        'scaling_info': position.get('scaling_info', None)
                    }
                    trades.append(trade)
                    
                    position = None
            
            # Look for new signals if no position
            if position is None:
                # Check if account is blown before looking for new signals
                if balance <= 0:
                    logging.warning(f"🔥 ACCOUNT BLOWN! Balance: ${balance:.2f} at {current_time}")
                    print(f"\n🔥 ACCOUNT BLOWN! Balance: ${balance:.2f}")
                    print(f"📅 Blown at: {current_time}")
                    print(f"📊 Total trades before blow: {len(trades)}")
                    break
                
                signal = self._get_signal(current_data, strategy_name, timeframe)
                
                if signal['signal'] in ['long', 'short']:
                    # Calculate position size
                    position_size = self._calculate_position_size(balance, signal, initial_balance)
                    
                    if position_size > 0:
                        # Apply position scaling if enabled
                        scaled_position_size = position_size
                        scaling_info = None
                        
                        if scaling_enabled:
                            # Calculate current account R:R
                            current_profit = balance - initial_balance
                            current_rr = current_profit / (initial_balance * 0.01)  # 1% = 1R
                            
                            if current_rr >= scaling_threshold_rr:
                                # Scale up position size
                                current_scaling_multiplier = scaling_risk_multiplier
                                scaled_position_size = position_size * current_scaling_multiplier
                                scaling_info = {
                                    'enabled': True,
                                    'current_rr': current_rr,
                                    'threshold': scaling_threshold_rr,
                                    'multiplier': current_scaling_multiplier,
                                    'original_size': position_size,
                                    'scaled_size': scaled_position_size
                                }
                            else:
                                # Reset to normal risk
                                current_scaling_multiplier = 1.0
                                scaling_info = {
                                    'enabled': True,
                                    'current_rr': current_rr,
                                    'threshold': scaling_threshold_rr,
                                    'multiplier': current_scaling_multiplier,
                                    'original_size': position_size,
                                    'scaled_size': scaled_position_size
                                }
                        
                        # Calculate take profit that compensates for trading fees
                        reward_ratio = 3  # Default 1:3 RR, can be made configurable
                        adjusted_take_profit = self._calculate_take_profit_with_fees(
                            current_price, signal['stop_loss'], reward_ratio, scaled_position_size
                        )
                        
                        position = {
                            'side': signal['signal'],
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'strategy': signal['strategy'],
                            'stop_loss': signal['stop_loss'],
                            'take_profit': adjusted_take_profit,
                            'position_size': scaled_position_size,
                            'scaling_info': scaling_info
                        }
                        
                        # Add trailing trigger if available and not None
                        if 'trailing_trigger' in signal and signal['trailing_trigger'] is not None:
                            position['trailing_trigger'] = signal['trailing_trigger']
            
            # Record equity
            equity_curve.append({
                'time': current_time,
                'balance': balance,
                'position_value': self._get_position_value(position, current_price) if position else 0
            })
        
        # Close any remaining position
        # Close any remaining position at the end (only if account not blown)
        if position is not None and balance > 0:
            final_price = data.iloc[-1]['close']
            pnl = self._calculate_pnl(position, final_price)
            balance += pnl
            
            # Count as stop loss for remaining position
            exit_counters['stop_loss'] += 1
            
            trade = {
                'entry_time': position['entry_time'],
                'exit_time': data.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'side': position['side'],
                'strategy': position['strategy'],
                'stop_loss': position['stop_loss'],
                'take_profit': position['take_profit'],
                'position_size': position['position_size'],
                'exit_type': 'stop_loss',
                'pnl': pnl,
                'balance': balance,
                'scaling_info': position.get('scaling_info', None)
            }
            trades.append(trade)
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades, initial_balance, equity_curve)
        
        # Create balance history from trades
        balance_history = []
        for trade in trades:
            scaling_details = ''
            if trade.get('scaling_info'):
                scaling = trade['scaling_info']
                if scaling['enabled']:
                    scaling_details = f" (Scale: {scaling['multiplier']}x, R:R: {scaling['current_rr']:.1f})"
            
            balance_history.append({
                'date': trade['exit_time'].strftime('%Y-%m-%d %H:%M'),
                'type': trade['side'].upper(),
                'entry_price': trade['entry_price'],
                'exit_price': trade['exit_price'],
                'stop_loss': trade['stop_loss'],
                'take_profit': trade['take_profit'],
                'position_size': trade['position_size'],
                'pnl': trade['pnl'],
                'balance': trade['balance'],
                'scaling_details': scaling_details
            })
        
        # Check if account was blown
        account_blown = balance <= 0
        
        self.results = {
            'trades': trades,
            'equity_curve': equity_curve,
            'metrics': metrics,
            'exit_counters': exit_counters,
            'final_balance': balance,
            'total_return': ((balance - initial_balance) / initial_balance) * 100,
            'balance_history': balance_history,
            'account_blown': account_blown
        }
        
        if account_blown:
            logging.warning(f"Backtest completed with ACCOUNT BLOWN! Final balance: {balance:.2f}, Return: {self.results['total_return']:.2f}%")
        else:
            logging.info(f"Backtest completed. Final balance: {balance:.2f}, Return: {self.results['total_return']:.2f}%")
        
        return self.results
    
    def _fetch_historical_data(self, symbol, start_date, end_date, timeframe='1h'):
        """Fetch historical OHLCV data with caching"""
        try:
            # Use cached data fetcher
            data = self.cached_fetcher.get_ohlcv_cached(
                symbol, timeframe, start_date, end_date, max_age_hours=24
            )
            
            if data.empty:
                logging.error("No historical data available")
                return pd.DataFrame()
            
            return data
            
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
        
        # Add candlestick patterns
        candlestick_patterns = self.indicators.calculate_candlestick_patterns(
            data['open'], data['high'], data['low'], data['close']
        )
        data = pd.concat([data, candlestick_patterns], axis=1)
        
        # Add divergence indicators
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        macd = self.indicators.calculate_macd(data['close'], 12, 26, 9)
        
        # Calculate divergence signals (optimized with shorter period)
        rsi_divergence = self.indicators.calculate_divergence(data['close'], rsi, 10)
        volume_divergence = self.indicators.calculate_volume_divergence(data['close'], data['volume'], 10)
        macd_divergence = self.indicators.calculate_macd_divergence(data['close'], macd['macd'], 10)
        
        # Combine all divergence signals
        divergence_signals = pd.concat([rsi_divergence, volume_divergence, macd_divergence], axis=1)
        data = pd.concat([data, divergence_signals], axis=1)
        
        return data
    
    def _get_signal(self, data, strategy_name, timeframe='1h'):
        """Get trading signal from specified strategy"""
        if strategy_name == 'all':
            return self.strategies.get_best_signal(data, timeframe)
        elif strategy_name == 'ema_rsi' or strategy_name.startswith('ema_rsi_'):
            # Parse ema_rsi parameters
            reverse_signal = False
            if strategy_name.startswith('ema_rsi_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.ema_rsi_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # For ema_rsi strategy, maintain 1R = $10 by recalculating stop loss
                entry_price = signal['entry_price']
                if signal['signal'] == 'long':
                    # Long: stop loss = entry_price - 10
                    signal['stop_loss'] = entry_price - 10
                else:
                    # Short: stop loss = entry_price + 10
                    signal['stop_loss'] = entry_price + 10
                
                # Recalculate take profit based on new stop loss
                risk = abs(entry_price - signal['stop_loss'])  # Should be $10
                if signal['signal'] == 'long':
                    signal['take_profit'] = entry_price + (risk * 3)  # 1:3 RR
                else:
                    signal['take_profit'] = entry_price - (risk * 3)  # 1:3 RR
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'bollinger_stochastic' or strategy_name.startswith('bollinger_stochastic_'):
            # Parse bollinger_stochastic parameters
            reverse_signal = False
            if strategy_name.startswith('bollinger_stochastic_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.bollinger_stochastic_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'macd_vwap' or strategy_name.startswith('macd_vwap_'):
            # Parse macd_vwap parameters
            reverse_signal = False
            if strategy_name.startswith('macd_vwap_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.macd_vwap_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'ichimoku' or strategy_name.startswith('ichimoku_'):
            # Parse ichimoku parameters
            reverse_signal = False
            if strategy_name.startswith('ichimoku_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.ichimoku_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'vsa_obv' or strategy_name.startswith('vsa_obv_'):
            # Parse vsa_obv parameters
            reverse_signal = False
            if strategy_name.startswith('vsa_obv_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.vsa_obv_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'multi_indicator' or strategy_name.startswith('multi_indicator_'):
            # Parse multi_indicator parameters
            reverse_signal = False
            if strategy_name.startswith('multi_indicator_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.multi_indicator_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'ema_rsi_ichimoku' or strategy_name.startswith('ema_rsi_ichimoku_'):
            # Parse ema_rsi_ichimoku parameters
            reverse_signal = False
            if strategy_name.startswith('ema_rsi_ichimoku_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.ema_rsi_ichimoku_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal

        elif strategy_name == 'enhanced_with_candlestick' or strategy_name.startswith('enhanced_with_candlestick_'):
            # Parse enhanced_with_candlestick parameters
            reverse_signal = False
            if strategy_name.startswith('enhanced_with_candlestick_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.enhanced_strategy_with_candlestick(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name.startswith('flexible_'):
            # Parse flexible strategy parameters
            parts = strategy_name.split('_')
            if len(parts) >= 3:
                strategy_timeframe = parts[1]
                mode = parts[2]
                return self.strategies.flexible_strategy(data, strategy_timeframe, mode)
            else:
                return self.strategies.flexible_strategy(data, timeframe, 'conservative')
        elif strategy_name.startswith('simple_'):
            # Parse simple strategy parameters
            parts = strategy_name.split('_')
            if len(parts) >= 3:
                strategy_timeframe = parts[1]
                mode = parts[2]
                return self.strategies.simple_strategy(data, strategy_timeframe, mode)
            else:
                return self.strategies.simple_strategy(data, timeframe, 'conservative')
        elif strategy_name == 'divergence_strategy' or strategy_name.startswith('divergence_strategy_'):
            # Parse divergence_strategy parameters
            reverse_signal = False
            if strategy_name.startswith('divergence_strategy_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.divergence_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'simple_divergence_strategy' or strategy_name.startswith('simple_divergence_strategy_'):
            # Parse simple_divergence_strategy parameters
            reverse_signal = False
            if strategy_name.startswith('simple_divergence_strategy_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.simple_divergence_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'wyckoff_vsa' or strategy_name.startswith('wyckoff_vsa_'):
            # Parse wyckoff_vsa parameters
            reverse_signal = False
            if strategy_name.startswith('wyckoff_vsa_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.wyckoff_vsa_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'practical_wyckoff_vsa' or strategy_name.startswith('practical_wyckoff_vsa_'):
            # Parse practical_wyckoff_vsa parameters
            reverse_signal = False
            if strategy_name.startswith('practical_wyckoff_vsa_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.practical_wyckoff_vsa_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'simple_test_strategy' or strategy_name.startswith('simple_test_strategy_'):
            # Parse simple_test_strategy parameters
            reverse_signal = False
            if strategy_name.startswith('simple_test_strategy_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = self.strategies.simple_test_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'ultra_simple_strategy' or strategy_name.startswith('ultra_simple_strategy_'):
            # Parse ultra_simple_strategy parameters
            if strategy_name.startswith('ultra_simple_strategy_'):
                # Format: ultra_simple_strategy_atr1.0_rr2.0_trail1.5_reverse
                parts = strategy_name.split('_')
                atr_multiplier = 1.5  # default
                reward_ratio = 3.0    # default
                trailing_ratio = 1.0  # default
                reverse_signal = False  # default
                
                for part in parts:
                    if part.startswith('atr'):
                        try:
                            atr_multiplier = float(part[3:])
                        except ValueError:
                            pass
                    elif part.startswith('rr'):
                        try:
                            reward_ratio = float(part[2:])
                        except ValueError:
                            pass
                    elif part.startswith('trail'):
                        try:
                            trailing_ratio = float(part[5:])
                        except ValueError:
                            pass
                    elif part == 'reverse':
                        reverse_signal = True
                
                signal = self.strategies.ultra_simple_strategy(
                    data, timeframe, atr_multiplier, reward_ratio, trailing_ratio
                )
                
                # Apply reverse signal logic if enabled
                if reverse_signal and signal['signal'] != 'no_signal':
                    # Swap signal direction
                    if signal['signal'] == 'long':
                        signal['signal'] = 'short'
                    else:
                        signal['signal'] = 'long'
                    
                    # Swap stop loss and take profit
                    original_stop_loss = signal['stop_loss']
                    original_take_profit = signal['take_profit']
                    
                    signal['stop_loss'] = original_take_profit
                    signal['take_profit'] = original_stop_loss
                    
                    # Update indicators
                    signal['indicators']['signal_reversed'] = True
                    signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
                
                return signal
            else:
                return self.strategies.ultra_simple_strategy(data, timeframe)
        elif strategy_name == 'smart_tp_strategy' or strategy_name.startswith('smart_tp_strategy_'):
            # Import smart TP strategies
            from strategies.strategies_smart_tp import SmartTPStrategies
            smart_strategies = SmartTPStrategies()
            
            # Parse smart_tp_strategy parameters
            reverse_signal = False
            if strategy_name.startswith('smart_tp_strategy_'):
                # Format: smart_tp_strategy_min1.5_max5.0_reverse
                parts = strategy_name.split('_')
                min_rr = 1.5  # default
                max_rr = 5.0  # default
                
                for part in parts:
                    if part.startswith('min'):
                        try:
                            min_rr = float(part[3:])
                        except ValueError:
                            pass
                    elif part.startswith('max'):
                        try:
                            max_rr = float(part[3:])
                        except ValueError:
                            pass
                    elif part == 'reverse':
                        reverse_signal = True
                
                signal = smart_strategies.smart_tp_strategy(
                    data, timeframe, min_rr, max_rr
                )
                
                # Apply reverse signal logic if enabled
                if reverse_signal and signal['signal'] != 'no_signal':
                    # Swap signal direction
                    if signal['signal'] == 'long':
                        signal['signal'] = 'short'
                    else:
                        signal['signal'] = 'long'
                    
                    # Swap stop loss and take profit
                    original_stop_loss = signal['stop_loss']
                    original_take_profit = signal['take_profit']
                    
                    signal['stop_loss'] = original_take_profit
                    signal['take_profit'] = original_stop_loss
                    
                    # Update indicators
                    signal['indicators']['signal_reversed'] = True
                    signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
                
                return signal
            else:
                signal = smart_strategies.smart_tp_strategy(data, timeframe)
                
                # Apply reverse signal logic if enabled
                if reverse_signal and signal['signal'] != 'no_signal':
                    # Swap signal direction
                    if signal['signal'] == 'long':
                        signal['signal'] = 'short'
                    else:
                        signal['signal'] = 'long'
                    
                    # Swap stop loss and take profit
                    original_stop_loss = signal['stop_loss']
                    original_take_profit = signal['take_profit']
                    
                    signal['stop_loss'] = original_take_profit
                    signal['take_profit'] = original_stop_loss
                    
                    # Update indicators
                    signal['indicators']['signal_reversed'] = True
                    signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
                
                return signal
        elif strategy_name == 'adaptive_tp_strategy' or strategy_name.startswith('adaptive_tp_strategy_'):
            # Import smart TP strategies
            from strategies.strategies_smart_tp import SmartTPStrategies
            smart_strategies = SmartTPStrategies()
            
            # Parse adaptive_tp_strategy parameters
            reverse_signal = False
            if strategy_name.startswith('adaptive_tp_strategy_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = smart_strategies.adaptive_tp_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'smc_strategy' or strategy_name.startswith('smc_strategy_'):
            # Import SMC strategies
            from strategies.strategies_smc import SMCStrategies
            smc_strategies = SMCStrategies()
            
            # Parse smc_strategy parameters
            if strategy_name.startswith('smc_strategy_'):
                # Format: smc_strategy_min1.5_max4.0_reverse
                parts = strategy_name.split('_')
                min_rr = 1.5  # default
                max_rr = 4.0  # default
                reverse_signal = False  # default
                
                for part in parts:
                    if part.startswith('min'):
                        try:
                            min_rr = float(part[3:])
                        except ValueError:
                            pass
                    elif part.startswith('max'):
                        try:
                            max_rr = float(part[3:])
                        except ValueError:
                            pass
                    elif part == 'reverse':
                        reverse_signal = True
                
                return smc_strategies.smc_strategy(
                    data, timeframe, min_rr, max_rr, reverse_signal
                )
            else:
                return smc_strategies.smc_strategy(data, timeframe)
        elif strategy_name == 'breaker_block_strategy' or strategy_name.startswith('breaker_block_strategy_'):
            # Import SMC strategies
            from strategies.strategies_smc import SMCStrategies
            smc_strategies = SMCStrategies()
            
            # Parse breaker_block_strategy parameters
            reverse_signal = False
            if strategy_name.startswith('breaker_block_strategy_'):
                parts = strategy_name.split('_')
                if 'reverse' in parts:
                    reverse_signal = True
            
            signal = smc_strategies.breaker_block_strategy(data, timeframe)
            
            # Apply reverse signal logic if enabled
            if reverse_signal and signal['signal'] != 'no_signal':
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                else:
                    signal['signal'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['signal_reversed'] = True
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
            
            return signal
        elif strategy_name == 'always_lose_strategy':
            # Custom strategy for testing account blown scenario
            if hasattr(self.strategies, 'always_lose_strategy'):
                return self.strategies.always_lose_strategy(data, timeframe)
            else:
                return {'signal': 'no_signal', 'reason': 'always_lose_strategy not found'}
        else:
            return {'signal': 'no_signal', 'reason': 'Invalid strategy'}
    
    def _calculate_position_size(self, balance, signal, initial_balance):
        """Calculate position size based on risk management"""
        
        # Check if strategy specifies account risk percentage
        if 'account_risk_percent' in signal:
            # Use strategy-specific risk percentage
            risk_percentage = signal['account_risk_percent'] / 100.0
        else:
            # Use default risk percentage from config
            risk_percentage = self.config.MAX_RISK_PER_TRADE
        
        # Use initial balance for fixed risk amount (not current balance)
        risk_amount = initial_balance * risk_percentage
        
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0
        
        # Calculate position size to risk exactly the specified amount
        position_size = risk_amount / price_diff
        
        # For ema_rsi strategy or always_lose_strategy, ensure exact risk calculation by not applying position size limits
        if 'ema_rsi_strategy' in signal.get('strategy', '') or signal.get('strategy') == 'always_lose_strategy':
            return position_size
        
        # Apply position size limits for other strategies
        max_position_value = balance * self.config.MAX_POSITION_SIZE
        max_position_size = max_position_value / entry_price
        
        return min(position_size, max_position_size)
    
    def _should_close_position(self, position, current_price, current_data):
        """Check if position should be closed with trailing stop support"""
        if position['side'] == 'long':
            # Check trailing stop trigger first (before other checks)
            if 'trailing_trigger' in position and current_price >= position['trailing_trigger']:
                # Move stop loss to entry price (breakeven)
                position['stop_loss'] = position['entry_price']
                # Remove trailing trigger to avoid repeated checks
                position.pop('trailing_trigger', None)
                # Don't close position yet, just update stop loss
                return False
            
            # Check stop loss
            if current_price <= position['stop_loss']:
                # Check if stop loss is at entry (trailing stop)
                if abs(position['stop_loss'] - position['entry_price']) < 0.01:
                    return 'stop_loss_at_entry'
                else:
                    return 'stop_loss'
            # Check take profit
            if current_price >= position['take_profit']:
                return 'take_profit'
        else:  # short
            # Check trailing stop trigger first (before other checks)
            if 'trailing_trigger' in position and current_price <= position['trailing_trigger']:
                # Move stop loss to entry price (breakeven)
                position['stop_loss'] = position['entry_price']
                # Remove trailing trigger to avoid repeated checks
                position.pop('trailing_trigger', None)
                # Don't close position yet, just update stop loss
                return False
            
            # Check stop loss
            if current_price >= position['stop_loss']:
                # Check if stop loss is at entry (trailing stop)
                if abs(position['stop_loss'] - position['entry_price']) < 0.01:
                    return 'stop_loss_at_entry'
                else:
                    return 'stop_loss'
            # Check take profit
            if current_price <= position['take_profit']:
                return 'take_profit'
        
        return False
    
    def _calculate_pnl(self, position, current_price):
        """Calculate PnL for a position including trading fees"""
        if position['side'] == 'long':
            pnl = (current_price - position['entry_price']) * position['position_size']
        else:
            pnl = (position['entry_price'] - current_price) * position['position_size']
        
        # Calculate trading fees: configurable rate of entry position value
        entry_value = position['entry_price'] * position['position_size']
        trading_fee = entry_value * self.config.TRADING_FEE_RATE
        
        # Subtract trading fee from PnL
        pnl_after_fees = pnl - trading_fee
        
        return pnl_after_fees
    
    def _calculate_take_profit_with_fees(self, entry_price, stop_loss, reward_ratio, position_size):
        """
        Calculate take profit that compensates for trading fees
        """
        risk = abs(entry_price - stop_loss)
        
        # Calculate gross profit needed for desired R:R
        gross_profit_needed = risk * reward_ratio
        
        # Calculate trading fee
        entry_value = entry_price * position_size
        trading_fee = entry_value * self.config.TRADING_FEE_RATE
        
        # Net profit needed = gross profit - trading fee
        net_profit_needed = gross_profit_needed - trading_fee
        
        # If net profit is negative, we need to increase gross profit
        if net_profit_needed <= 0:
            # Calculate minimum gross profit needed to cover fees
            min_gross_profit = trading_fee + (risk * 0.1)  # At least 0.1R profit
            net_profit_needed = min_gross_profit - trading_fee
        
        # Calculate take profit price
        if entry_price > stop_loss:  # Long position
            take_profit = entry_price + (net_profit_needed / position_size)
        else:  # Short position
            take_profit = entry_price - (net_profit_needed / position_size)
        
        return take_profit
    
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
                'avg_trade': 0,  # Add this field
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
            'avg_trade': average_pnl,  # Alias for compatibility
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
