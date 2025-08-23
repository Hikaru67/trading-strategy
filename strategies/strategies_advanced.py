import pandas as pd
import numpy as np
from indicators import TechnicalIndicators

class AdvancedStrategies:
    def __init__(self, config=None):
        self.config = config
        self.indicators = TechnicalIndicators()
    
    def ichimoku_strategy(self, data, timeframe='1h'):
        """
        Ichimoku Kinko Hyo Strategy
        """
        if len(data) < 52:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate Ichimoku
        ichimoku = self.indicators.calculate_ichimoku(data['high'], data['low'], data['close'])
        
        current_price = data['close'].iloc[-1]
        tenkan = ichimoku['tenkan_sen'].iloc[-1]
        kijun = ichimoku['kijun_sen'].iloc[-1]
        senkou_a = ichimoku['senkou_span_a'].iloc[-1]
        senkou_b = ichimoku['senkou_span_b'].iloc[-1]
        
        # Long signal: Price above cloud, tenkan > kijun
        if (current_price > senkou_a and current_price > senkou_b and
            tenkan > kijun):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 2)
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'ichimoku_strategy',
                'confidence': 0.7,
                'indicators': {
                    'ichimoku_tenkan': tenkan,
                    'ichimoku_kijun': kijun,
                    'ichimoku_senkou_a': senkou_a,
                    'ichimoku_senkou_b': senkou_b,
                    'current_price': current_price
                }
            }
        
        # Short signal: Price below cloud, tenkan < kijun
        elif (current_price < senkou_a and current_price < senkou_b and
              tenkan < kijun):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 2)
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'ichimoku_strategy',
                'confidence': 0.7,
                'indicators': {
                    'ichimoku_tenkan': tenkan,
                    'ichimoku_kijun': kijun,
                    'ichimoku_senkou_a': senkou_a,
                    'ichimoku_senkou_b': senkou_b,
                    'current_price': current_price
                }
            }
        
        return {'signal': 'no_signal', 'reason': 'No Ichimoku signal'}
    
    def vsa_obv_strategy(self, data, timeframe='1h'):
        """
        VSA + OBV Strategy
        """
        if len(data) < 20:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate VSA and OBV
        vsa_signals = self.indicators.calculate_vsa_signals(
            data['open'], data['high'], data['low'], data['close'], data['volume']
        )
        obv = self.indicators.calculate_obv(data['close'], data['volume'])
        
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Long signal: Accumulation + rising OBV
        if (vsa_signals['accumulation'].iloc[-1] and
            obv.iloc[-1] > obv.iloc[-5] and
            current_volume > avg_volume * 1.5):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'vsa_obv_strategy',
                'confidence': 0.8
            }
        
        # Short signal: Distribution + falling OBV
        elif (vsa_signals['distribution'].iloc[-1] and
              obv.iloc[-1] < obv.iloc[-5] and
              current_volume > avg_volume * 1.5):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'vsa_obv_strategy',
                'confidence': 0.8
            }
        
        return {'signal': 'no_signal', 'reason': 'No VSA+OBV signal'}
    
    def multi_indicator_strategy(self, data, timeframe='1h'):
        """
        Multi-Indicator Strategy
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate multiple indicators
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        macd = self.indicators.calculate_macd(data['close'], 12, 26, 9)
        
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd['macd'].iloc[-1]
        current_signal = macd['signal'].iloc[-1]
        
        # Long signal: Multiple confirmations
        if (current_ema_20 > current_ema_50 and
            30 < current_rsi < 70 and
            current_macd > current_signal):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'multi_indicator_strategy',
                'confidence': 0.8
            }
        
        # Short signal: Multiple confirmations
        elif (current_ema_20 < current_ema_50 and
              30 < current_rsi < 70 and
              current_macd < current_signal):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'multi_indicator_strategy',
                'confidence': 0.8
            }
        
        return {'signal': 'no_signal', 'reason': 'No multi-indicator signal'}
    
    def ema_rsi_ichimoku_strategy(self, data, timeframe='1h'):
        """
        EMA + RSI + Ichimoku Strategy
        """
        if len(data) < 52:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        ichimoku = self.indicators.calculate_ichimoku(data['high'], data['low'], data['close'])
        
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        senkou_a = ichimoku['senkou_span_a'].iloc[-1]
        senkou_b = ichimoku['senkou_span_b'].iloc[-1]
        
        # Long signal: All indicators bullish
        if (current_ema_20 > current_ema_50 and
            30 < current_rsi < 70 and
            current_price > senkou_a and current_price > senkou_b):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'ema_rsi_ichimoku_strategy',
                'confidence': 0.85
            }
        
        # Short signal: All indicators bearish
        elif (current_ema_20 < current_ema_50 and
              30 < current_rsi < 70 and
              current_price < senkou_a and current_price < senkou_b):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'ema_rsi_ichimoku_strategy',
                'confidence': 0.85
            }
        
        return {'signal': 'no_signal', 'reason': 'No EMA+RSI+Ichimoku signal'}
    
    def enhanced_strategy_with_candlestick(self, data, timeframe='1h'):
        """
        Enhanced Strategy with Candlestick Confirmation
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators and patterns
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        patterns = self.indicators.calculate_candlestick_patterns(
            data['open'], data['high'], data['low'], data['close']
        )
        
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Check for bullish candlestick patterns
        bullish_patterns = [
            patterns['hammer'].iloc[-1],
            patterns['pinbar_bullish'].iloc[-1],
            patterns['bullish_engulfing'].iloc[-1]
        ]
        
        # Check for bearish candlestick patterns
        bearish_patterns = [
            patterns['shooting_star'].iloc[-1],
            patterns['pinbar_bearish'].iloc[-1],
            patterns['bearish_engulfing'].iloc[-1]
        ]
        
        # Long signal: Trend + RSI + Bullish pattern
        if (current_ema_20 > current_ema_50 and
            30 < current_rsi < 70 and
            any(bullish_patterns)):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'enhanced_strategy_with_candlestick',
                'confidence': 0.9
            }
        
        # Short signal: Trend + RSI + Bearish pattern
        elif (current_ema_20 < current_ema_50 and
              30 < current_rsi < 70 and
              any(bearish_patterns)):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'enhanced_strategy_with_candlestick',
                'confidence': 0.9
            }
        
        return {'signal': 'no_signal', 'reason': 'No enhanced strategy signal'}
    
    def flexible_strategy(self, data, timeframe='1h', mode='conservative'):
        """
        Flexible Strategy with different modes
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Get parameters based on mode and timeframe
        if mode == 'conservative':
            rsi_oversold = 25
            rsi_overbought = 75
            volume_multiplier = 1.5
        else:  # aggressive
            rsi_oversold = 30
            rsi_overbought = 70
            volume_multiplier = 1.2
        
        # Calculate indicators
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Volume confirmation
        volume_ok = current_volume > avg_volume * volume_multiplier
        
        # Long signal
        if (current_ema_20 > current_ema_50 and
            current_rsi < rsi_oversold and
            volume_ok):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': f'flexible_strategy_{mode}',
                'confidence': 0.8
            }
        
        # Short signal
        elif (current_ema_20 < current_ema_50 and
              current_rsi > rsi_overbought and
              volume_ok):
            
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': f'flexible_strategy_{mode}',
                'confidence': 0.8
            }
        
        return {'signal': 'no_signal', 'reason': 'No flexible strategy signal'}
    
    def simple_strategy(self, data, timeframe='1h', mode='conservative'):
        """
        Simple Strategy for high signal generation
        """
        if len(data) < 20:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate simple indicators
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        
        current_price = data['close'].iloc[-1]
        current_ema_20 = ema_20.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Simple conditions
        if mode == 'conservative':
            # Long: Price above EMA, RSI oversold
            if current_price > current_ema_20 and current_rsi < 30:
                atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
                stop_loss = current_price - (atr * 1.5)
                entry_price = current_price
                risk = entry_price - stop_loss
                take_profit = entry_price + (risk * 3)
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': f'simple_strategy_{mode}',
                    'confidence': 0.6
                }
            
            # Short: Price below EMA, RSI overbought
            elif current_price < current_ema_20 and current_rsi > 70:
                atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
                stop_loss = current_price + (atr * 1.5)
                entry_price = current_price
                risk = stop_loss - entry_price
                take_profit = entry_price - (risk * 3)
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': f'simple_strategy_{mode}',
                    'confidence': 0.6
                }
        else:  # aggressive
            # More relaxed conditions
            if current_price > current_ema_20 and current_rsi < 40:
                atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
                stop_loss = current_price - (atr * 1.5)
                entry_price = current_price
                risk = entry_price - stop_loss
                take_profit = entry_price + (risk * 3)
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': f'simple_strategy_{mode}',
                    'confidence': 0.5
                }
            
            elif current_price < current_ema_20 and current_rsi > 60:
                atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
                stop_loss = current_price + (atr * 1.5)
                entry_price = current_price
                risk = stop_loss - entry_price
                take_profit = entry_price - (risk * 3)
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': f'simple_strategy_{mode}',
                    'confidence': 0.5
                }
        
        return {'signal': 'no_signal', 'reason': 'No simple strategy signal'}
    
    def wyckoff_vsa_strategy(self, data, timeframe='1h'):
        """
        Wyckoff VSA Strategy
        """
        if len(data) < 100:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # This is a simplified version - full implementation would be complex
        # For now, return no signal to avoid errors
        return {'signal': 'no_signal', 'reason': 'Wyckoff VSA not implemented'}
    
    def practical_wyckoff_vsa_strategy(self, data, timeframe='1h'):
        """
        Practical Wyckoff VSA Strategy
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # This is a simplified version - full implementation would be complex
        # For now, return no signal to avoid errors
        return {'signal': 'no_signal', 'reason': 'Practical Wyckoff VSA not implemented'}
