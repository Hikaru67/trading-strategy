import pandas as pd
import numpy as np
from indicators import BasicIndicators
from indicators import CandlestickPatterns

class BasicStrategies:
    def __init__(self):
        self.indicators = BasicIndicators()
        self.patterns = CandlestickPatterns()
    
    def ultra_simple_strategy(self, data, timeframe='1h', atr_multiplier=1.5, reward_ratio=3.0, trailing_ratio=1.0):
        """
        Ultra Simple Strategy with Risk-Based Position Sizing
        Target: Generate signals with minimal conditions + 1% account risk per trade
        
        Args:
            data: OHLCV data
            timeframe: Trading timeframe
            atr_multiplier: ATR multiplier for stop loss (default: 1.5) - NOT USED anymore
            reward_ratio: Risk:Reward ratio for take profit (default: 3.0 = 1:3)
            trailing_ratio: Risk:Reward ratio for trailing stop trigger (default: 1.0 = 1:1)
        """
        if len(data) < 10:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Get current price and previous candle data
        current_price = data['close'].iloc[-1]
        previous_price = data['close'].iloc[-2]
        previous_low = data['low'].iloc[-2]   # Đáy cây nến trước đó
        previous_high = data['high'].iloc[-2] # Đỉnh cây nến trước đó
        
        # Ultra simple condition: if price went up, go long
        if current_price > previous_price:
            # Use previous candle's low as stop loss
            entry_price = current_price
            stop_loss = previous_low  # Stop loss = đáy cây nến trước đó
            risk_per_share = entry_price - stop_loss
            
            # Calculate take profit (configurable R:R)
            take_profit = entry_price + (risk_per_share * reward_ratio)
            
            # Only add trailing trigger if trailing_ratio > 0
            trailing_trigger = None
            if trailing_ratio > 0:
                trailing_trigger = entry_price + (risk_per_share * trailing_ratio)  # Configurable trailing trigger
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trailing_trigger': trailing_trigger if trailing_trigger is not None else None,
                'strategy': 'ultra_simple_strategy',
                'confidence': 0.5,
                'account_risk_percent': 1.0,  # Risk 1% of account
                'indicators': {
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'previous_low': previous_low,
                    'stop_loss_method': 'previous_candle_low',
                    'timeframe': timeframe,
                    'risk_reward': f'1:{reward_ratio}',
                    'trailing_trigger_rr': f'1:{trailing_ratio}' if trailing_ratio > 0 else 'Disabled',
                    'trailing_trigger': f'{trailing_trigger:.2f} (R:R 1:{trailing_ratio})' if trailing_trigger is not None else 'Disabled'
                }
            }
        
        # If price went down, go short
        elif current_price < previous_price:
            # Use previous candle's high as stop loss
            entry_price = current_price
            stop_loss = previous_high  # Stop loss = đỉnh cây nến trước đó
            risk_per_share = stop_loss - entry_price
            
            # Calculate take profit (configurable R:R)
            take_profit = entry_price - (risk_per_share * reward_ratio)
            
            # Only add trailing trigger if trailing_ratio > 0
            trailing_trigger = None
            if trailing_ratio > 0:
                trailing_trigger = entry_price - (risk_per_share * trailing_ratio)  # Configurable trailing trigger
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trailing_trigger': trailing_trigger if trailing_trigger is not None else None,
                'strategy': 'ultra_simple_strategy',
                'confidence': 0.5,
                'account_risk_percent': 1.0,  # Risk 1% of account
                'indicators': {
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'previous_high': previous_high,
                    'stop_loss_method': 'previous_candle_high',
                    'timeframe': timeframe,
                    'risk_reward': f'1:{reward_ratio}',
                    'trailing_trigger_rr': f'1:{trailing_ratio}' if trailing_ratio > 0 else 'Disabled',
                    'trailing_trigger': f'{trailing_trigger:.2f} (R:R 1:{trailing_ratio})' if trailing_trigger is not None else 'Disabled'
                }
            }
        
        return {'signal': 'no_signal', 'reason': 'No price movement'}
    
    def simple_test_strategy(self, data, timeframe='1h'):
        """
        Simple Test Strategy with Relaxed Conditions
        Target: Generate more signals for testing
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Check for NaN values
        if pd.isna(current_ema_20) or pd.isna(current_rsi):
            return {'signal': 'no_signal', 'reason': 'NaN values in indicators'}
        
        # Simple conditions (relaxed)
        if current_price > current_ema_20 and current_rsi < 70:
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'simple_test_strategy',
                    'confidence': 0.6,
                    'indicators': {
                        'ema_20': current_ema_20,
                        'rsi': current_rsi,
                        'timeframe': timeframe
                    }
                }
        
        elif current_price < current_ema_20 and current_rsi > 30:
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            
            if risk > 0:
                take_profit = entry_price - (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'simple_test_strategy',
                    'confidence': 0.6,
                    'indicators': {
                        'ema_20': current_ema_20,
                        'rsi': current_rsi,
                        'timeframe': timeframe
                    }
                }
        
        return {'signal': 'no_signal', 'reason': 'No simple test signal'}
    


    def ema_rsi_strategy(self, data, timeframe='1h'):
        """
        EMA + RSI Strategy
        Target: Trend following with momentum confirmation
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Long signal: Price above both EMAs, RSI oversold bounce
        if (current_price > current_ema_20 > current_ema_50 and 
            30 < current_rsi < 70):
            
            # Calculate 1:3 RR with fixed 1% account risk
            entry_price = current_price
            # Fixed $10 stop loss (1R = 1% of $1000 account)
            stop_loss = entry_price - 10  # $10 below entry
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'ema_rsi_strategy',
                    'confidence': 0.7,
                    'account_risk_percent': 1.0,  # Fixed 1% account risk
                    'indicators': {
                        'ema_20': current_ema_20,
                        'ema_50': current_ema_50,
                        'rsi': current_rsi,
                        'timeframe': timeframe
                    }
                }
        
        # Short signal: Price below both EMAs, RSI overbought rejection
        elif (current_price < current_ema_20 < current_ema_50 and 
              30 < current_rsi < 70):
            
            # Calculate 1:3 RR with fixed 1% account risk
            entry_price = current_price
            # Fixed $10 stop loss (1R = 1% of $1000 account)
            stop_loss = entry_price + 10  # $10 above entry
            risk = stop_loss - entry_price
            
            if risk > 0:
                take_profit = entry_price - (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'ema_rsi_strategy',
                    'confidence': 0.7,
                    'account_risk_percent': 1.0,  # Fixed 1% account risk
                    'indicators': {
                        'ema_20': current_ema_20,
                        'ema_50': current_ema_50,
                        'rsi': current_rsi,
                        'timeframe': timeframe
                    }
                }
        
        return {'signal': 'no_signal', 'reason': 'No EMA+RSI signal'}
    
    def bollinger_stochastic_strategy(self, data, timeframe='1h'):
        """
        Bollinger Bands + Stochastic Strategy
        Target: Mean reversion with momentum confirmation
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        bb = self.indicators.calculate_bollinger_bands(data['close'], 20, 2)
        stoch = self.indicators.calculate_stochastic(data['high'], data['low'], data['close'], 14, 3, 3)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_bb_upper = bb['upper'].iloc[-1]
        current_bb_lower = bb['lower'].iloc[-1]
        current_stoch_k = stoch['k'].iloc[-1]
        current_stoch_d = stoch['d'].iloc[-1]
        
        # Long signal: Price near lower BB, stochastic oversold
        if (current_price <= current_bb_lower * 1.02 and 
            current_stoch_k < 20 and current_stoch_d < 20):
            
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'bollinger_stochastic_strategy',
                    'confidence': 0.7,
                    'indicators': {
                        'bb_upper': current_bb_upper,
                        'bb_lower': current_bb_lower,
                        'stoch_k': current_stoch_k,
                        'stoch_d': current_stoch_d,
                        'timeframe': timeframe
                    }
                }
        
        # Short signal: Price near upper BB, stochastic overbought
        elif (current_price >= current_bb_upper * 0.98 and 
              current_stoch_k > 80 and current_stoch_d > 80):
            
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            
            if risk > 0:
                take_profit = entry_price - (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'bollinger_stochastic_strategy',
                    'confidence': 0.7,
                    'indicators': {
                        'bb_upper': current_bb_upper,
                        'bb_lower': current_bb_lower,
                        'stoch_k': current_stoch_k,
                        'stoch_d': current_stoch_d,
                        'timeframe': timeframe
                    }
                }
        
        return {'signal': 'no_signal', 'reason': 'No Bollinger+Stochastic signal'}
    
    def macd_vwap_strategy(self, data, timeframe='1h'):
        """
        MACD + VWAP Strategy
        Target: Trend following with volume confirmation
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        macd = self.indicators.calculate_macd(data['close'], 12, 26, 9)
        vwap = self.indicators.calculate_vwap(data['high'], data['low'], data['close'], data['volume'])
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_macd = macd['macd'].iloc[-1]
        current_signal = macd['signal'].iloc[-1]
        current_vwap = vwap.iloc[-1]
        
        # Long signal: MACD bullish crossover, price above VWAP
        if (current_macd > current_signal and 
            macd['macd'].iloc[-2] <= macd['signal'].iloc[-2] and  # Crossover
            current_price > current_vwap):
            
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'macd_vwap_strategy',
                    'confidence': 0.7,
                    'indicators': {
                        'macd': current_macd,
                        'signal': current_signal,
                        'vwap': current_vwap,
                        'timeframe': timeframe
                    }
                }
        
        # Short signal: MACD bearish crossover, price below VWAP
        elif (current_macd < current_signal and 
              macd['macd'].iloc[-2] >= macd['signal'].iloc[-2] and  # Crossover
              current_price < current_vwap):
            
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            
            if risk > 0:
                take_profit = entry_price - (risk * 3)  # 1:3 RR
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'macd_vwap_strategy',
                    'confidence': 0.7,
                    'indicators': {
                        'macd': current_macd,
                        'signal': current_signal,
                        'vwap': current_vwap,
                        'timeframe': timeframe
                    }
                }
        
        return {'signal': 'no_signal', 'reason': 'No MACD+VWAP signal'}
