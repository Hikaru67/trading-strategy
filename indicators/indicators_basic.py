import pandas as pd
import numpy as np
import ta

class BasicIndicators:
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
    def calculate_atr(high, low, close, period=14):
        """Calculate Average True Range"""
        return ta.volatility.average_true_range(high, low, close, window=period)
    
    @staticmethod
    def calculate_obv(close, volume):
        """Calculate On Balance Volume"""
        return ta.volume.on_balance_volume(close, volume)
