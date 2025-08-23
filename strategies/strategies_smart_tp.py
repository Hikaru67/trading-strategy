#!/usr/bin/env python3
"""
Smart Take Profit Strategy
Dự đoán điểm TP dựa trên các yếu tố thị trường thay vì cố định R:R
"""

import pandas as pd
import numpy as np
from indicators.indicators_basic import BasicIndicators

class SmartTPStrategies:
    def __init__(self):
        self.indicators = BasicIndicators()
    
    def smart_tp_strategy(self, data, timeframe='1h', min_rr=1.5, max_rr=5.0):
        """
        Smart Take Profit Strategy
        Dự đoán điểm TP dựa trên:
        1. Volatility (ATR)
        2. Support/Resistance levels
        3. Volume profile
        4. Trend strength
        5. Market structure
        
        Args:
            data: OHLCV data
            timeframe: Trading timeframe
            min_rr: Minimum Risk:Reward ratio (default: 1.5)
            max_rr: Maximum Risk:Reward ratio (default: 5.0)
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Get current price and previous candle data
        current_price = data['close'].iloc[-1]
        previous_price = data['close'].iloc[-2]
        previous_low = data['low'].iloc[-2]
        previous_high = data['high'].iloc[-2]
        
        # Calculate indicators for TP prediction
        atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
        bb = self.indicators.calculate_bollinger_bands(data['close'], 20, 2)
        rsi = self.indicators.calculate_rsi(data['close'], 14).iloc[-1]
        volume_sma = data['volume'].rolling(20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        
        # Ultra simple condition: if price went up, go long
        if current_price > previous_price:
            entry_price = current_price
            stop_loss = previous_low
            risk_per_share = entry_price - stop_loss
            
            # Predict TP based on market conditions
            predicted_rr = self._predict_rr_ratio(data, 'long', atr, bb, rsi, current_volume, volume_sma)
            predicted_rr = max(min_rr, min(max_rr, predicted_rr))  # Clamp to min/max
            
            take_profit = entry_price + (risk_per_share * predicted_rr)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'smart_tp_strategy',
                'confidence': 0.6,
                'account_risk_percent': 1.0,
                'indicators': {
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'previous_low': previous_low,
                    'stop_loss_method': 'previous_candle_low',
                    'predicted_rr': predicted_rr,
                    'tp_method': 'smart_prediction',
                    'timeframe': timeframe,
                    'atr': atr,
                    'rsi': rsi,
                    'volume_ratio': current_volume / volume_sma,
                    'bb_position': (current_price - bb['lower'].iloc[-1]) / (bb['upper'].iloc[-1] - bb['lower'].iloc[-1])
                }
            }
        
        # If price went down, go short
        elif current_price < previous_price:
            entry_price = current_price
            stop_loss = previous_high
            risk_per_share = stop_loss - entry_price
            
            # Predict TP based on market conditions
            predicted_rr = self._predict_rr_ratio(data, 'short', atr, bb, rsi, current_volume, volume_sma)
            predicted_rr = max(min_rr, min(max_rr, predicted_rr))  # Clamp to min/max
            
            take_profit = entry_price - (risk_per_share * predicted_rr)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'smart_tp_strategy',
                'confidence': 0.6,
                'account_risk_percent': 1.0,
                'indicators': {
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'previous_high': previous_high,
                    'stop_loss_method': 'previous_candle_high',
                    'predicted_rr': predicted_rr,
                    'tp_method': 'smart_prediction',
                    'timeframe': timeframe,
                    'atr': atr,
                    'rsi': rsi,
                    'volume_ratio': current_volume / volume_sma,
                    'bb_position': (current_price - bb['lower'].iloc[-1]) / (bb['upper'].iloc[-1] - bb['lower'].iloc[-1])
                }
            }
        
        return {'signal': 'no_signal', 'reason': 'No price movement'}
    
    def _predict_rr_ratio(self, data, direction, atr, bb, rsi, current_volume, volume_sma):
        """
        Predict optimal R:R ratio based on market conditions
        
        Args:
            data: OHLCV data
            direction: 'long' or 'short'
            atr: Current ATR value
            bb: Bollinger Bands data
            rsi: Current RSI value
            current_volume: Current volume
            volume_sma: Volume SMA
            
        Returns:
            float: Predicted R:R ratio
        """
        # Base R:R ratio
        base_rr = 2.0
        
        # 1. Volatility factor (ATR-based)
        avg_atr = data['high'].rolling(20).mean() - data['low'].rolling(20).mean()
        avg_atr = avg_atr.iloc[-1]
        volatility_factor = atr / avg_atr if avg_atr > 0 else 1.0
        
        # Higher volatility = higher potential R:R
        if volatility_factor > 1.2:
            base_rr += 0.5
        elif volatility_factor < 0.8:
            base_rr -= 0.3
        
        # 2. Bollinger Bands position factor
        bb_width = bb['upper'].iloc[-1] - bb['lower'].iloc[-1]
        bb_position = (data['close'].iloc[-1] - bb['lower'].iloc[-1]) / bb_width if bb_width > 0 else 0.5
        
        if direction == 'long':
            # For long: closer to upper band = lower R:R potential
            if bb_position > 0.8:
                base_rr -= 0.4
            elif bb_position < 0.2:
                base_rr += 0.3
        else:  # short
            # For short: closer to lower band = lower R:R potential
            if bb_position < 0.2:
                base_rr -= 0.4
            elif bb_position > 0.8:
                base_rr += 0.3
        
        # 3. RSI factor
        if direction == 'long':
            if rsi < 30:  # Oversold
                base_rr += 0.4
            elif rsi > 70:  # Overbought
                base_rr -= 0.3
        else:  # short
            if rsi > 70:  # Overbought
                base_rr += 0.4
            elif rsi < 30:  # Oversold
                base_rr -= 0.3
        
        # 4. Volume factor
        volume_ratio = current_volume / volume_sma
        if volume_ratio > 1.5:  # High volume
            base_rr += 0.3
        elif volume_ratio < 0.7:  # Low volume
            base_rr -= 0.2
        
        # 5. Trend strength factor
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        
        trend_strength = abs(ema_20.iloc[-1] - ema_50.iloc[-1]) / ema_50.iloc[-1]
        
        if direction == 'long' and ema_20.iloc[-1] > ema_50.iloc[-1]:
            # Strong uptrend for long
            if trend_strength > 0.01:
                base_rr += 0.3
        elif direction == 'short' and ema_20.iloc[-1] < ema_50.iloc[-1]:
            # Strong downtrend for short
            if trend_strength > 0.01:
                base_rr += 0.3
        
        # 6. Support/Resistance factor
        recent_highs = data['high'].rolling(20).max()
        recent_lows = data['low'].rolling(20).min()
        
        current_price = data['close'].iloc[-1]
        
        if direction == 'long':
            # Distance to recent high
            distance_to_high = (recent_highs.iloc[-1] - current_price) / current_price
            if distance_to_high > 0.02:  # Far from resistance
                base_rr += 0.2
            elif distance_to_high < 0.005:  # Near resistance
                base_rr -= 0.3
        else:  # short
            # Distance to recent low
            distance_to_low = (current_price - recent_lows.iloc[-1]) / current_price
            if distance_to_low > 0.02:  # Far from support
                base_rr += 0.2
            elif distance_to_low < 0.005:  # Near support
                base_rr -= 0.3
        
        return max(1.0, base_rr)  # Minimum 1:1 R:R
    
    def adaptive_tp_strategy(self, data, timeframe='1h'):
        """
        Adaptive Take Profit Strategy
        Sử dụng machine learning đơn giản để dự đoán TP
        """
        if len(data) < 100:
            return {'signal': 'no_signal', 'reason': 'Insufficient data for adaptive strategy'}
        
        # Get current price and previous candle data
        current_price = data['close'].iloc[-1]
        previous_price = data['close'].iloc[-2]
        previous_low = data['low'].iloc[-2]
        previous_high = data['high'].iloc[-2]
        
        # Calculate multiple indicators
        atr = self.indicators.calculate_atr(data['high'], data['low'], data['close'], 14).iloc[-1]
        bb = self.indicators.calculate_bollinger_bands(data['close'], 20, 2)
        rsi = self.indicators.calculate_rsi(data['close'], 14).iloc[-1]
        macd = self.indicators.calculate_macd(data['close'], 12, 26, 9)
        stoch = self.indicators.calculate_stochastic(data['high'], data['low'], data['close'], 14)
        
        # Volume analysis
        volume_sma = data['volume'].rolling(20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        volume_ratio = current_volume / volume_sma
        
        # Trend analysis
        ema_20 = self.indicators.calculate_ema(data['close'], 20)
        ema_50 = self.indicators.calculate_ema(data['close'], 50)
        trend_direction = 1 if ema_20.iloc[-1] > ema_50.iloc[-1] else -1
        
        # Ultra simple condition: if price went up, go long
        if current_price > previous_price:
            entry_price = current_price
            stop_loss = previous_low
            risk_per_share = entry_price - stop_loss
            
            # Adaptive TP calculation
            predicted_rr = self._adaptive_rr_prediction(
                data, 'long', atr, bb, rsi, macd, stoch, 
                volume_ratio, trend_direction
            )
            
            take_profit = entry_price + (risk_per_share * predicted_rr)
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'adaptive_tp_strategy',
                'confidence': 0.7,
                'account_risk_percent': 1.0,
                'indicators': {
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'previous_low': previous_low,
                    'stop_loss_method': 'previous_candle_low',
                    'predicted_rr': predicted_rr,
                    'tp_method': 'adaptive_prediction',
                    'timeframe': timeframe,
                    'atr': atr,
                    'rsi': rsi,
                    'volume_ratio': volume_ratio,
                    'trend_direction': trend_direction,
                    'macd_signal': 'bullish' if macd['macd'].iloc[-1] > macd['signal'].iloc[-1] else 'bearish',
                    'stoch_k': stoch['k'].iloc[-1],
                    'bb_position': (current_price - bb['lower'].iloc[-1]) / (bb['upper'].iloc[-1] - bb['lower'].iloc[-1])
                }
            }
        
        # If price went down, go short
        elif current_price < previous_price:
            entry_price = current_price
            stop_loss = previous_high
            risk_per_share = stop_loss - entry_price
            
            # Adaptive TP calculation
            predicted_rr = self._adaptive_rr_prediction(
                data, 'short', atr, bb, rsi, macd, stoch, 
                volume_ratio, trend_direction
            )
            
            take_profit = entry_price - (risk_per_share * predicted_rr)
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'adaptive_tp_strategy',
                'confidence': 0.7,
                'account_risk_percent': 1.0,
                'indicators': {
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'previous_high': previous_high,
                    'stop_loss_method': 'previous_candle_high',
                    'predicted_rr': predicted_rr,
                    'tp_method': 'adaptive_prediction',
                    'timeframe': timeframe,
                    'atr': atr,
                    'rsi': rsi,
                    'volume_ratio': volume_ratio,
                    'trend_direction': trend_direction,
                    'macd_signal': 'bullish' if macd['macd'].iloc[-1] > macd['signal'].iloc[-1] else 'bearish',
                    'stoch_k': stoch['k'].iloc[-1],
                    'bb_position': (current_price - bb['lower'].iloc[-1]) / (bb['upper'].iloc[-1] - bb['lower'].iloc[-1])
                }
            }
        
        return {'signal': 'no_signal', 'reason': 'No price movement'}
    
    def _adaptive_rr_prediction(self, data, direction, atr, bb, rsi, macd, stoch, volume_ratio, trend_direction):
        """
        Advanced adaptive R:R prediction using multiple factors
        """
        # Base R:R
        base_rr = 2.5
        
        # Factor weights
        weights = {
            'volatility': 0.25,
            'momentum': 0.20,
            'volume': 0.15,
            'trend': 0.20,
            'support_resistance': 0.20
        }
        
        # 1. Volatility factor
        volatility_score = 0
        avg_atr = data['high'].rolling(20).mean() - data['low'].rolling(20).mean()
        avg_atr = avg_atr.iloc[-1]
        
        if avg_atr > 0:
            atr_ratio = atr / avg_atr
            if atr_ratio > 1.3:
                volatility_score = 1.0  # High volatility
            elif atr_ratio > 1.0:
                volatility_score = 0.5  # Medium volatility
            else:
                volatility_score = 0.0  # Low volatility
        
        # 2. Momentum factor
        momentum_score = 0
        
        # RSI momentum
        if direction == 'long':
            if rsi < 30:
                momentum_score += 0.5
            elif rsi > 70:
                momentum_score -= 0.3
        else:  # short
            if rsi > 70:
                momentum_score += 0.5
            elif rsi < 30:
                momentum_score -= 0.3
        
        # MACD momentum
        macd_bullish = macd['macd'].iloc[-1] > macd['signal'].iloc[-1]
        if (direction == 'long' and macd_bullish) or (direction == 'short' and not macd_bullish):
            momentum_score += 0.3
        
        # Stochastic momentum
        stoch_k = stoch['k'].iloc[-1]
        if direction == 'long' and stoch_k < 30:
            momentum_score += 0.2
        elif direction == 'short' and stoch_k > 70:
            momentum_score += 0.2
        
        # 3. Volume factor
        volume_score = 0
        if volume_ratio > 1.5:
            volume_score = 1.0
        elif volume_ratio > 1.2:
            volume_score = 0.5
        elif volume_ratio < 0.7:
            volume_score = -0.3
        
        # 4. Trend factor
        trend_score = 0
        if (direction == 'long' and trend_direction > 0) or (direction == 'short' and trend_direction < 0):
            trend_score = 1.0
        elif (direction == 'long' and trend_direction < 0) or (direction == 'short' and trend_direction > 0):
            trend_score = -0.5
        
        # 5. Support/Resistance factor
        sr_score = 0
        recent_highs = data['high'].rolling(20).max()
        recent_lows = data['low'].rolling(20).min()
        current_price = data['close'].iloc[-1]
        
        if direction == 'long':
            distance_to_high = (recent_highs.iloc[-1] - current_price) / current_price
            if distance_to_high > 0.03:
                sr_score = 1.0  # Far from resistance
            elif distance_to_high > 0.01:
                sr_score = 0.5  # Medium distance
            else:
                sr_score = -0.5  # Near resistance
        else:  # short
            distance_to_low = (current_price - recent_lows.iloc[-1]) / current_price
            if distance_to_low > 0.03:
                sr_score = 1.0  # Far from support
            elif distance_to_low > 0.01:
                sr_score = 0.5  # Medium distance
            else:
                sr_score = -0.5  # Near support
        
        # Calculate weighted score
        total_score = (
            volatility_score * weights['volatility'] +
            momentum_score * weights['momentum'] +
            volume_score * weights['volume'] +
            trend_score * weights['trend'] +
            sr_score * weights['support_resistance']
        )
        
        # Convert score to R:R ratio
        # Score range: -1 to 1
        # R:R range: 1.5 to 4.0
        predicted_rr = 2.75 + (total_score * 1.25)
        
        return max(1.5, min(4.0, predicted_rr))
