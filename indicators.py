import pandas as pd
import numpy as np
import ta

class TechnicalIndicators:
    @staticmethod
    def calculate_ema(data, period):
        """Calculate Exponential Moving Average"""
        return ta.trend.ema_indicator(data, window=period)
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """Calculate Relative Strength Index"""
        return ta.momentum.rsi(data, window=period)
    
    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        bb = ta.volatility.BollingerBands(data, window=period, window_dev=std_dev)
        return {
            'upper': bb.bollinger_hband(),
            'middle': bb.bollinger_mavg(),
            'lower': bb.bollinger_lband()
        }
    
    @staticmethod
    def calculate_stochastic(high, low, close, period=14, smooth_k=3, smooth_d=3):
        """Calculate Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(high, low, close, window=period, smooth_window=smooth_k)
        return {
            'k': stoch.stoch(),
            'd': stoch.stoch_signal()
        }
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        macd = ta.trend.MACD(data, window_fast=fast, window_slow=slow, window_sign=signal)
        return {
            'macd': macd.macd(),
            'signal': macd.macd_signal(),
            'histogram': macd.macd_diff()
        }
    
    @staticmethod
    def calculate_vwap(high, low, close, volume):
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    @staticmethod
    def calculate_ichimoku(high, low, close, tenkan=9, kijun=26, senkou_b=52):
        """Calculate Ichimoku Cloud"""
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (high.rolling(window=tenkan).max() + low.rolling(window=tenkan).min()) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (high.rolling(window=kijun).max() + low.rolling(window=kijun).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((high.rolling(window=senkou_b).max() + low.rolling(window=senkou_b).min()) / 2).shift(kijun)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-kijun)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Calculate Average True Range"""
        return ta.volatility.average_true_range(high, low, close, window=period)
    
    @staticmethod
    def calculate_obv(close, volume):
        """Calculate On Balance Volume"""
        return ta.volume.on_balance_volume(close, volume)
    
    @staticmethod
    def calculate_vsa_signals(open_price, high, low, close, volume, period=20):
        """Calculate Volume Spread Analysis signals"""
        # Calculate average volume
        avg_volume = volume.rolling(window=period).mean()
        
        # Calculate price spread
        price_spread = high - low
        
        # Calculate average spread
        avg_spread = price_spread.rolling(window=period).mean()
        
        # VSA signals
        vsa_signals = pd.DataFrame(index=close.index)
        
        # High volume up bar
        vsa_signals['high_volume_up'] = (
            (volume > avg_volume * 1.5) & 
            (close > open_price) & 
            (price_spread > avg_spread)
        )
        
        # High volume down bar
        vsa_signals['high_volume_down'] = (
            (volume > avg_volume * 1.5) & 
            (close < open_price) & 
            (price_spread > avg_spread)
        )
        
        # Low volume up bar
        vsa_signals['low_volume_up'] = (
            (volume < avg_volume * 0.7) & 
            (close > open_price)
        )
        
        # Low volume down bar
        vsa_signals['low_volume_down'] = (
            (volume < avg_volume * 0.7) & 
            (close < open_price)
        )
        
        return vsa_signals
