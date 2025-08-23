import pandas as pd
import numpy as np
from indicators import BasicIndicators
from indicators import AdvancedIndicators
from indicators import CandlestickPatterns

class DivergenceStrategies:
    def __init__(self):
        self.indicators = BasicIndicators()
        self.advanced_indicators = AdvancedIndicators()
        self.patterns = CandlestickPatterns()
    
    def simple_divergence_strategy(self, data, timeframe='1h'):
        """
        Simple Divergence Strategy: Only requires divergence OR candlestick patterns
        Target: More signals for testing
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        macd = self.indicators.calculate_macd(data['close'], 12, 26, 9)
        
        # Calculate divergence signals
        rsi_divergence = self.advanced_indicators.calculate_divergence_simple(data['close'], rsi, 10)
        volume_divergence = self.advanced_indicators.calculate_volume_divergence(data['close'], data['volume'], 10)
        macd_divergence = self.advanced_indicators.calculate_macd_divergence(data['close'], macd['macd'], 10)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Check for bullish signals (divergence OR candlestick)
        bullish_divergence = (
            rsi_divergence['bullish_divergence'].iloc[-1] or
            rsi_divergence['hidden_bullish_divergence'].iloc[-1] or
            volume_divergence['bullish_volume_divergence'].iloc[-1] or
            macd_divergence['macd_bullish_divergence'].iloc[-1]
        )
        
        bullish_candlestick = (
            data['hammer'].iloc[-1] or
            data['pinbar_bullish'].iloc[-1] or
            data['bullish_engulfing'].iloc[-1] or
            data['morning_star'].iloc[-1] or
            data['tweezer_bottom'].iloc[-1]
        )
        
        # Check for bearish signals (divergence OR candlestick)
        bearish_divergence = (
            rsi_divergence['bearish_divergence'].iloc[-1] or
            rsi_divergence['hidden_bearish_divergence'].iloc[-1] or
            volume_divergence['bearish_volume_divergence'].iloc[-1] or
            macd_divergence['macd_bearish_divergence'].iloc[-1]
        )
        
        bearish_candlestick = (
            data['shooting_star'].iloc[-1] or
            data['pinbar_bearish'].iloc[-1] or
            data['bearish_engulfing'].iloc[-1] or
            data['evening_star'].iloc[-1] or
            data['tweezer_top'].iloc[-1]
        )
        
        # Volume confirmation (reduced threshold)
        volume_ok = current_volume > avg_volume * 0.5
        
        # Long signal: (Bullish divergence OR bullish candlestick) AND volume
        if (bullish_divergence or bullish_candlestick) and volume_ok:
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 3)  # 1:3 RR
                
                signal_type = []
                if bullish_divergence: signal_type.append('Divergence')
                if bullish_candlestick: signal_type.append('Candlestick')
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'simple_divergence_strategy',
                    'confidence': 0.7,
                    'indicators': {
                        'signal_type': ' + '.join(signal_type),
                        'volume_ratio': f'{current_volume/avg_volume:.2f}x',
                        'timeframe': timeframe,
                        'method': 'simple_or_logic'
                    }
                }
        
        # Short signal: (Bearish divergence OR bearish candlestick) AND volume
        elif (bearish_divergence or bearish_candlestick) and volume_ok:
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            
            if risk > 0:
                take_profit = entry_price - (risk * 3)  # 1:3 RR
                
                signal_type = []
                if bearish_divergence: signal_type.append('Divergence')
                if bearish_candlestick: signal_type.append('Candlestick')
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'simple_divergence_strategy',
                    'confidence': 0.7,
                    'indicators': {
                        'signal_type': ' + '.join(signal_type),
                        'volume_ratio': f'{current_volume/avg_volume:.2f}x',
                        'timeframe': timeframe,
                        'method': 'simple_or_logic'
                    }
                }
        
        return {'signal': 'no_signal', 'reason': 'No divergence or candlestick signal with volume confirmation'}

    def divergence_strategy(self, data, timeframe='1h'):
        """
        Divergence Strategy: Combines divergence signals with candlestick reversal patterns
        Target: High-quality reversal signals with strong confirmation
        Uses Advanced Divergence Detection based on Pine Script logic
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        macd = self.indicators.calculate_macd(data['close'], 12, 26, 9)
        
        # Calculate divergence signals using advanced method (based on Pine Script)
        rsi_divergence = self.advanced_indicators.calculate_divergence_simple(data['close'], rsi, 10)
        volume_divergence = self.advanced_indicators.calculate_volume_divergence(data['close'], data['volume'], 10)
        macd_divergence = self.advanced_indicators.calculate_macd_divergence(data['close'], macd['macd'], 10)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Check for bullish divergence signals (including hidden)
        bullish_divergence_signals = [
            rsi_divergence['bullish_divergence'].iloc[-1],
            rsi_divergence['hidden_bullish_divergence'].iloc[-1],
            volume_divergence['bullish_volume_divergence'].iloc[-1],
            macd_divergence['macd_bullish_divergence'].iloc[-1]
        ]
        
        # Check for bearish divergence signals (including hidden)
        bearish_divergence_signals = [
            rsi_divergence['bearish_divergence'].iloc[-1],
            rsi_divergence['hidden_bearish_divergence'].iloc[-1],
            volume_divergence['bearish_volume_divergence'].iloc[-1],
            macd_divergence['macd_bearish_divergence'].iloc[-1]
        ]
        
        # Check for candlestick reversal patterns
        bullish_candlestick_patterns = [
            data['hammer'].iloc[-1],
            data['pinbar_bullish'].iloc[-1],
            data['bullish_engulfing'].iloc[-1],
            data['morning_star'].iloc[-1],
            data['tweezer_bottom'].iloc[-1]
        ]
        
        bearish_candlestick_patterns = [
            data['shooting_star'].iloc[-1],
            data['pinbar_bearish'].iloc[-1],
            data['bearish_engulfing'].iloc[-1],
            data['evening_star'].iloc[-1],
            data['tweezer_top'].iloc[-1]
        ]
        
        # Volume confirmation (reduced threshold for more signals)
        volume_ok = current_volume > avg_volume * 0.8
        
        # Long signal: Bullish divergence + bullish candlestick + volume
        if any(bullish_divergence_signals) and any(bullish_candlestick_patterns) and volume_ok:
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price - (atr * 1.5)
            entry_price = current_price
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 3)  # 1:3 RR
                
                # Identify which divergence and pattern triggered
                divergence_names = []
                if rsi_divergence['bullish_divergence'].iloc[-1]: divergence_names.append('RSI Bullish')
                if rsi_divergence['hidden_bullish_divergence'].iloc[-1]: divergence_names.append('RSI Hidden Bullish')
                if volume_divergence['bullish_volume_divergence'].iloc[-1]: divergence_names.append('Volume Bullish')
                if macd_divergence['macd_bullish_divergence'].iloc[-1]: divergence_names.append('MACD Bullish')
                
                pattern_names = []
                if data['hammer'].iloc[-1]: pattern_names.append('Hammer')
                if data['pinbar_bullish'].iloc[-1]: pattern_names.append('Pinbar')
                if data['bullish_engulfing'].iloc[-1]: pattern_names.append('Engulfing')
                if data['morning_star'].iloc[-1]: pattern_names.append('Morning Star')
                if data['tweezer_bottom'].iloc[-1]: pattern_names.append('Tweezer Bottom')
                
                return {
                    'signal': 'long',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'divergence_strategy',
                    'confidence': 0.9,
                    'indicators': {
                        'divergence': ', '.join(divergence_names),
                        'pattern': ', '.join(pattern_names),
                        'volume_ratio': f'{current_volume/avg_volume:.2f}x',
                        'timeframe': timeframe,
                        'method': 'advanced_pine_script'
                    }
                }
        
        # Short signal: Bearish divergence + bearish candlestick + volume
        elif any(bearish_divergence_signals) and any(bearish_candlestick_patterns) and volume_ok:
            # Calculate 1:3 RR
            atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
            stop_loss = current_price + (atr * 1.5)
            entry_price = current_price
            risk = stop_loss - entry_price
            
            if risk > 0:
                take_profit = entry_price - (risk * 3)  # 1:3 RR
                
                # Identify which divergence and pattern triggered
                divergence_names = []
                if rsi_divergence['bearish_divergence'].iloc[-1]: divergence_names.append('RSI Bearish')
                if rsi_divergence['hidden_bearish_divergence'].iloc[-1]: divergence_names.append('RSI Hidden Bearish')
                if volume_divergence['bearish_volume_divergence'].iloc[-1]: divergence_names.append('Volume Bearish')
                if macd_divergence['macd_bearish_divergence'].iloc[-1]: divergence_names.append('MACD Bearish')
                
                pattern_names = []
                if data['shooting_star'].iloc[-1]: pattern_names.append('Shooting Star')
                if data['pinbar_bearish'].iloc[-1]: pattern_names.append('Pinbar')
                if data['bearish_engulfing'].iloc[-1]: pattern_names.append('Engulfing')
                if data['evening_star'].iloc[-1]: pattern_names.append('Evening Star')
                if data['tweezer_top'].iloc[-1]: pattern_names.append('Tweezer Top')
                
                return {
                    'signal': 'short',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'strategy': 'divergence_strategy',
                    'confidence': 0.9,
                    'indicators': {
                        'divergence': ', '.join(divergence_names),
                        'pattern': ', '.join(pattern_names),
                        'volume_ratio': f'{current_volume/avg_volume:.2f}x',
                        'timeframe': timeframe,
                        'method': 'advanced_pine_script'
                    }
                }
        
        return {'signal': 'no_signal', 'reason': 'No divergence signal with candlestick confirmation'}
