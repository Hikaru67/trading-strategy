import pandas as pd
import numpy as np
from indicators import TechnicalIndicators

class TradingStrategies:
    def __init__(self, config):
        self.config = config
        self.indicators = TechnicalIndicators()
    
    def ema_rsi_strategy(self, data, timeframe='1h'):
        """
        Strategy 1: EMA + RSI (trend + strength) - Optimized for 1H
        Target: 60%+ win rate with 1:3 RR
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        ema_fast = self.indicators.calculate_ema(data['close'], self.config.STRATEGY_PARAMS['ema']['fast'])
        ema_slow = self.indicators.calculate_ema(data['close'], self.config.STRATEGY_PARAMS['ema']['slow'])
        rsi = self.indicators.calculate_rsi(data['close'], self.config.STRATEGY_PARAMS['ema']['rsi_period'])
        
        # Get current values
        current_ema_fast = ema_fast.iloc[-1]
        current_ema_slow = ema_slow.iloc[-1]
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
        prev_prev_rsi = rsi.iloc[-3] if len(rsi) > 2 else prev_rsi
        
        # Additional filters for higher win rate
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Volume confirmation
        volume_ok = current_volume > avg_volume * 1.2
        
        # RSI momentum confirmation
        rsi_momentum_up = current_rsi > prev_rsi > prev_prev_rsi
        rsi_momentum_down = current_rsi < prev_rsi < prev_prev_rsi
        
        # Check for long signal with stricter conditions
        if (current_ema_fast > current_ema_slow * 1.001 and  # Strong trend
            self.config.STRATEGY_PARAMS['ema']['rsi_oversold'] <= current_rsi <= 35 and  # More conservative
            rsi_momentum_up and  # RSI momentum
            volume_ok and  # Volume confirmation
            current_price > ema_fast.iloc[-1]):  # Price above fast EMA
            
            # Calculate 1:3 RR
            stop_loss = data['low'].iloc[-10:].min() * 0.995  # Conservative stop
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)  # 1:3 RR
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'ema_rsi',
                'confidence': 0.85
            }
        
        # Check for short signal with stricter conditions
        elif (current_ema_fast < current_ema_slow * 0.999 and  # Strong trend
              self.config.STRATEGY_PARAMS['ema']['rsi_overbought'] >= current_rsi >= 65 and  # More conservative
              rsi_momentum_down and  # RSI momentum
              volume_ok and  # Volume confirmation
              current_price < ema_fast.iloc[-1]):  # Price below fast EMA
            
            # Calculate 1:3 RR
            stop_loss = data['high'].iloc[-10:].max() * 1.005  # Conservative stop
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)  # 1:3 RR
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'ema_rsi',
                'confidence': 0.85
            }
        
        return {'signal': 'no_signal', 'reason': 'No EMA+RSI signal'}
    
    def bollinger_stochastic_strategy(self, data, timeframe='1h'):
        """
        Strategy 2: Bollinger Bands + Stochastic - Optimized for 1H
        Target: 60%+ win rate with 1:3 RR
        """
        if len(data) < 20:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        bb = self.indicators.calculate_bollinger_bands(
            data['close'], 
            self.config.STRATEGY_PARAMS['bollinger']['period'],
            self.config.STRATEGY_PARAMS['bollinger']['std_dev']
        )
        stoch = self.indicators.calculate_stochastic(
            data['high'], data['low'], data['close'],
            self.config.STRATEGY_PARAMS['bollinger']['stoch_period']
        )
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_stoch_k = stoch['k'].iloc[-1]
        current_stoch_d = stoch['d'].iloc[-1]
        prev_stoch_k = stoch['k'].iloc[-2] if len(stoch['k']) > 1 else current_stoch_k
        
        # Additional filters
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        volume_ok = current_volume > avg_volume * 1.3
        
        # Stochastic momentum
        stoch_momentum_up = current_stoch_k > prev_stoch_k and current_stoch_k > current_stoch_d
        stoch_momentum_down = current_stoch_k < prev_stoch_k and current_stoch_k < current_stoch_d
        
        # Check for long signal with stricter conditions
        if (current_price <= bb['lower'].iloc[-1] * 1.002 and  # Price near lower band
            current_stoch_k < self.config.STRATEGY_PARAMS['bollinger']['stoch_oversold'] and 
            current_stoch_d < self.config.STRATEGY_PARAMS['bollinger']['stoch_oversold'] and
            stoch_momentum_up and  # Stochastic momentum
            volume_ok):  # Volume confirmation
            
            # Calculate 1:3 RR
            stop_loss = bb['lower'].iloc[-1] * 0.995
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)  # 1:3 RR
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'bollinger_stochastic',
                'confidence': 0.8
            }
        
        # Check for short signal with stricter conditions
        elif (current_price >= bb['upper'].iloc[-1] * 0.998 and  # Price near upper band
              current_stoch_k > self.config.STRATEGY_PARAMS['bollinger']['stoch_overbought'] and 
              current_stoch_d > self.config.STRATEGY_PARAMS['bollinger']['stoch_overbought'] and
              stoch_momentum_down and  # Stochastic momentum
              volume_ok):  # Volume confirmation
            
            # Calculate 1:3 RR
            stop_loss = bb['upper'].iloc[-1] * 1.005
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)  # 1:3 RR
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'bollinger_stochastic',
                'confidence': 0.8
            }
        
        return {'signal': 'no_signal', 'reason': 'No Bollinger+Stochastic signal'}
    
    def macd_vwap_strategy(self, data, timeframe='5m'):
        """
        Strategy 3: MACD + VWAP (trend following money flow)
        
        Entry conditions:
        - Long: Price above VWAP + MACD histogram > 0 + MACD line crosses above Signal
        - Short: Price below VWAP + MACD histogram < 0 + MACD line crosses below Signal
        """
        if len(data) < 26:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        macd = self.indicators.calculate_macd(
            data['close'],
            self.config.STRATEGY_PARAMS['macd']['fast'],
            self.config.STRATEGY_PARAMS['macd']['slow'],
            self.config.STRATEGY_PARAMS['macd']['signal']
        )
        vwap = self.indicators.calculate_vwap(data['high'], data['low'], data['close'], data['volume'])
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_vwap = vwap.iloc[-1]
        current_macd = macd['macd'].iloc[-1]
        current_signal = macd['signal'].iloc[-1]
        current_histogram = macd['histogram'].iloc[-1]
        
        # Previous values for crossover detection
        prev_macd = macd['macd'].iloc[-2] if len(macd['macd']) > 1 else current_macd
        prev_signal = macd['signal'].iloc[-2] if len(macd['signal']) > 1 else current_signal
        
        # Check for long signal
        if (current_price > current_vwap and 
            current_histogram > 0 and
            prev_macd <= prev_signal and current_macd > current_signal):  # Bullish crossover
            
            return {
                'signal': 'long',
                'entry_price': current_price,
                'stop_loss': current_vwap * 0.995,  # Stop below VWAP
                'take_profit': current_price * (1 + self.config.TP_PERCENTAGES['swing']),
                'strategy': 'macd_vwap',
                'confidence': 0.75
            }
        
        # Check for short signal
        elif (current_price < current_vwap and 
              current_histogram < 0 and
              prev_macd >= prev_signal and current_macd < current_signal):  # Bearish crossover
            
            return {
                'signal': 'short',
                'entry_price': current_price,
                'stop_loss': current_vwap * 1.005,  # Stop above VWAP
                'take_profit': current_price * (1 - self.config.TP_PERCENTAGES['swing']),
                'strategy': 'macd_vwap',
                'confidence': 0.75
            }
        
        return {'signal': 'no_signal', 'reason': 'No MACD+VWAP signal'}
    
    def ichimoku_strategy(self, data, timeframe='5m'):
        """
        Strategy 4: Ichimoku Kinko Hyo (all-in-one indicator)
        
        Entry conditions:
        - Long: Price above cloud, Tenkan crosses above Kijun, Chikou span above price
        - Short: Price below cloud, Tenkan crosses below Kijun, Chikou span below price
        """
        if len(data) < 52:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate Ichimoku
        ichimoku = self.indicators.calculate_ichimoku(
            data['high'], data['low'], data['close'],
            self.config.STRATEGY_PARAMS['ichimoku']['tenkan'],
            self.config.STRATEGY_PARAMS['ichimoku']['kijun'],
            self.config.STRATEGY_PARAMS['ichimoku']['senkou_b']
        )
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_tenkan = ichimoku['tenkan_sen'].iloc[-1]
        current_kijun = ichimoku['kijun_sen'].iloc[-1]
        current_senkou_a = ichimoku['senkou_span_a'].iloc[-1]
        current_senkou_b = ichimoku['senkou_span_b'].iloc[-1]
        current_chikou = ichimoku['chikou_span'].iloc[-1]
        
        # Previous values for crossover detection
        prev_tenkan = ichimoku['tenkan_sen'].iloc[-2] if len(ichimoku['tenkan_sen']) > 1 else current_tenkan
        prev_kijun = ichimoku['kijun_sen'].iloc[-2] if len(ichimoku['kijun_sen']) > 1 else current_kijun
        
        # Determine cloud color
        cloud_top = max(current_senkou_a, current_senkou_b)
        cloud_bottom = min(current_senkou_a, current_senkou_b)
        
        # Check for long signal
        if (current_price > cloud_top and  # Price above cloud
            prev_tenkan <= prev_kijun and current_tenkan > current_kijun and  # Tenkan crosses above Kijun
            current_chikou > current_price):  # Chikou span above price
            
            return {
                'signal': 'long',
                'entry_price': current_price,
                'stop_loss': cloud_bottom * 0.995,  # Stop below cloud
                'take_profit': current_price * (1 + self.config.TP_PERCENTAGES['trend']),
                'strategy': 'ichimoku',
                'confidence': 0.85
            }
        
        # Check for short signal
        elif (current_price < cloud_bottom and  # Price below cloud
              prev_tenkan >= prev_kijun and current_tenkan < current_kijun and  # Tenkan crosses below Kijun
              current_chikou < current_price):  # Chikou span below price
            
            return {
                'signal': 'short',
                'entry_price': current_price,
                'stop_loss': cloud_top * 1.005,  # Stop above cloud
                'take_profit': current_price * (1 - self.config.TP_PERCENTAGES['trend']),
                'strategy': 'ichimoku',
                'confidence': 0.85
            }
        
        return {'signal': 'no_signal', 'reason': 'No Ichimoku signal'}
    
    def vsa_obv_strategy(self, data, timeframe='5m'):
        """
        Strategy 5: Volume Spread Analysis (VSA) + OBV (Volume Confirmation)
        
        Entry conditions:
        - Long: High volume up bar + OBV trending up
        - Short: High volume down bar + OBV trending down
        """
        if len(data) < 20:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate indicators
        vsa_signals = self.indicators.calculate_vsa_signals(
            data['open'], data['high'], data['low'], data['close'], data['volume']
        )
        obv = self.indicators.calculate_obv(data['close'], data['volume'])
        
        # Get current values
        current_vsa_high_up = vsa_signals['high_volume_up'].iloc[-1]
        current_vsa_high_down = vsa_signals['high_volume_down'].iloc[-1]
        current_obv = obv.iloc[-1]
        prev_obv = obv.iloc[-5] if len(obv) > 5 else current_obv
        
        # Check OBV trend (last 5 periods)
        obv_trending_up = current_obv > prev_obv
        obv_trending_down = current_obv < prev_obv
        
        # Check for long signal
        if current_vsa_high_up and obv_trending_up:
            return {
                'signal': 'long',
                'entry_price': data['close'].iloc[-1],
                'stop_loss': data['low'].iloc[-1] * 0.995,  # Stop below current low
                'take_profit': data['close'].iloc[-1] * (1 + self.config.TP_PERCENTAGES['swing']),
                'strategy': 'vsa_obv',
                'confidence': 0.8
            }
        
        # Check for short signal
        elif current_vsa_high_down and obv_trending_down:
            return {
                'signal': 'short',
                'entry_price': data['close'].iloc[-1],
                'stop_loss': data['high'].iloc[-1] * 1.005,  # Stop above current high
                'take_profit': data['close'].iloc[-1] * (1 - self.config.TP_PERCENTAGES['swing']),
                'strategy': 'vsa_obv',
                'confidence': 0.8
            }
        
        return {'signal': 'no_signal', 'reason': 'No VSA+OBV signal'}
    
    def get_all_signals(self, data, timeframe='5m'):
        """
        Get signals from all strategies
        
        Args:
            data: DataFrame with OHLCV data
            timeframe: Timeframe for analysis
        
        Returns:
            dict: All strategy signals
        """
        signals = {
            'ema_rsi': self.ema_rsi_strategy(data, timeframe),
            'bollinger_stochastic': self.bollinger_stochastic_strategy(data, timeframe),
            'macd_vwap': self.macd_vwap_strategy(data, timeframe),
            'ichimoku': self.ichimoku_strategy(data, timeframe),
            'vsa_obv': self.vsa_obv_strategy(data, timeframe)
        }
        
        return signals
    
    def get_best_signal(self, data, timeframe='1h'):
        """
        Get the best signal from all strategies based on confidence
        
        Args:
            data: DataFrame with OHLCV data
            timeframe: Timeframe for analysis
        
        Returns:
            dict: Best signal or no signal
        """
        all_signals = self.get_all_signals(data, timeframe)
        
        # Filter valid signals
        valid_signals = []
        for strategy_name, signal in all_signals.items():
            if signal['signal'] in ['long', 'short']:
                valid_signals.append((strategy_name, signal))
        
        if not valid_signals:
            return {'signal': 'no_signal', 'reason': 'No valid signals from any strategy'}
        
        # Sort by confidence and return the best
        valid_signals.sort(key=lambda x: x[1]['confidence'], reverse=True)
        best_strategy, best_signal = valid_signals[0]
        
        return {
            'signal': best_signal['signal'],
            'entry_price': best_signal['entry_price'],
            'stop_loss': best_signal['stop_loss'],
            'take_profit': best_signal['take_profit'],
            'strategy': best_strategy,
            'confidence': best_signal['confidence'],
            'all_signals': all_signals
        }
    
    def multi_indicator_strategy(self, data, timeframe='1h'):
        """
        Multi-Indicator Strategy - Combines all indicators for high accuracy
        Target: 60%+ win rate with 1:3 RR
        Uses weighted scoring system for signal confirmation
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        # Calculate all indicators
        ema_fast = self.indicators.calculate_ema(data['close'], 12)
        ema_slow = self.indicators.calculate_ema(data['close'], 26)
        rsi = self.indicators.calculate_rsi(data['close'], 14)
        bb = self.indicators.calculate_bollinger_bands(data['close'], 20, 2.5)
        macd = self.indicators.calculate_macd(data['close'], 8, 21, 5)
        vwap = self.indicators.calculate_vwap(data['high'], data['low'], data['close'], data['volume'])
        stoch = self.indicators.calculate_stochastic(data['high'], data['low'], data['close'], 14)
        obv = self.indicators.calculate_obv(data['close'], data['volume'])
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Initialize scoring system
        long_score = 0
        short_score = 0
        
        # 1. TREND ANALYSIS (Weight: 30%)
        # EMA trend
        if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
            long_score += 30
        else:
            short_score += 30
        
        # Price vs VWAP
        if current_price > vwap.iloc[-1]:
            long_score += 15
        else:
            short_score += 15
        
        # 2. MOMENTUM ANALYSIS (Weight: 25%)
        # RSI conditions
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
        
        if current_rsi < 30 and current_rsi > prev_rsi:  # Oversold + momentum up
            long_score += 25
        elif current_rsi > 70 and current_rsi < prev_rsi:  # Overbought + momentum down
            short_score += 25
        
        # 3. VOLATILITY ANALYSIS (Weight: 20%)
        # Bollinger Bands
        bb_width = (bb['upper'].iloc[-1] - bb['lower'].iloc[-1]) / bb['middle'].iloc[-1]
        
        if current_price <= bb['lower'].iloc[-1] * 1.01:  # Near lower band
            long_score += 20
        elif current_price >= bb['upper'].iloc[-1] * 0.99:  # Near upper band
            short_score += 20
        
        # 4. VOLUME ANALYSIS (Weight: 15%)
        # Volume confirmation
        volume_ratio = current_volume / avg_volume
        if volume_ratio > 1.2:
            if long_score > short_score:
                long_score += 15
            elif short_score > long_score:
                short_score += 15
        
        # 5. MACD CONFIRMATION (Weight: 10%)
        # MACD signal
        if (macd['macd'].iloc[-1] > macd['signal'].iloc[-1] and 
            macd['histogram'].iloc[-1] > macd['histogram'].iloc[-2]):
            long_score += 10
        elif (macd['macd'].iloc[-1] < macd['signal'].iloc[-1] and 
              macd['histogram'].iloc[-1] < macd['histogram'].iloc[-2]):
            short_score += 10
        
        # 6. STOCHASTIC CONFIRMATION (Weight: 10%)
        # Stochastic conditions
        stoch_k = stoch['k'].iloc[-1]
        stoch_d = stoch['d'].iloc[-1]
        
        if stoch_k < 20 and stoch_k > stoch_d:
            long_score += 10
        elif stoch_k > 80 and stoch_k < stoch_d:
            short_score += 10
        
        # 7. OBV TREND CONFIRMATION (Weight: 10%)
        # OBV trend
        obv_current = obv.iloc[-1]
        obv_prev = obv.iloc[-5] if len(obv) > 5 else obv_current
        
        if obv_current > obv_prev:
            long_score += 10
        else:
            short_score += 10
        
        # Determine signal based on scoring
        min_score_threshold = 70  # Minimum score to generate signal
        
        if long_score >= min_score_threshold and long_score > short_score + 20:
            # Calculate 1:3 RR for long
            stop_loss = min(data['low'].iloc[-10:].min(), bb['lower'].iloc[-1]) * 0.995
            entry_price = current_price
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 3)
            
            confidence = min(long_score / 100, 0.95)  # Cap confidence at 95%
            
            return {
                'signal': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'multi_indicator',
                'confidence': confidence,
                'score': long_score,
                'indicators': {
                    'trend': 'EMA + VWAP bullish',
                    'momentum': f'RSI {current_rsi:.1f}',
                    'volatility': f'BB width {bb_width:.3f}',
                    'volume': f'Volume ratio {volume_ratio:.2f}',
                    'macd': 'MACD bullish' if macd['macd'].iloc[-1] > macd['signal'].iloc[-1] else 'MACD bearish',
                    'stoch': f'Stoch K {stoch_k:.1f}, D {stoch_d:.1f}',
                    'obv': 'OBV trending up' if obv_current > obv_prev else 'OBV trending down'
                }
            }
        
        elif short_score >= min_score_threshold and short_score > long_score + 20:
            # Calculate 1:3 RR for short
            stop_loss = max(data['high'].iloc[-10:].max(), bb['upper'].iloc[-1]) * 1.005
            entry_price = current_price
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 3)
            
            confidence = min(short_score / 100, 0.95)  # Cap confidence at 95%
            
            return {
                'signal': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': 'multi_indicator',
                'confidence': confidence,
                'score': short_score,
                'indicators': {
                    'trend': 'EMA + VWAP bearish',
                    'momentum': f'RSI {current_rsi:.1f}',
                    'volatility': f'BB width {bb_width:.3f}',
                    'volume': f'Volume ratio {volume_ratio:.2f}',
                    'macd': 'MACD bullish' if macd['macd'].iloc[-1] > macd['signal'].iloc[-1] else 'MACD bearish',
                    'stoch': f'Stoch K {stoch_k:.1f}, D {stoch_d:.1f}',
                    'obv': 'OBV trending up' if obv_current > obv_prev else 'OBV trending down'
                }
            }
        
        return {
            'signal': 'no_signal', 
            'reason': f'No strong signal. Long score: {long_score}, Short score: {short_score}',
            'long_score': long_score,
            'short_score': short_score
        }
