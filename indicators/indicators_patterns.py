import pandas as pd
import numpy as np

class CandlestickPatterns:
    @staticmethod
    def calculate_candlestick_patterns(open_price, high, low, close):
        """Calculate various candlestick patterns"""
        patterns = pd.DataFrame(index=close.index)
        
        # Calculate basic candlestick properties
        body_size = abs(close - open_price)
        upper_shadow = high - np.maximum(open_price, close)
        lower_shadow = np.minimum(open_price, close) - low
        total_range = high - low
        
        # Doji patterns
        patterns['doji'] = body_size <= (total_range * 0.1)
        
        # Hammer and Shooting Star
        patterns['hammer'] = (
            (lower_shadow > body_size * 2) &  # Long lower shadow
            (upper_shadow < body_size * 0.5) &  # Short upper shadow
            (close > open_price)  # Bullish body
        )
        
        patterns['shooting_star'] = (
            (upper_shadow > body_size * 2) &  # Long upper shadow
            (lower_shadow < body_size * 0.5) &  # Short lower shadow
            (close < open_price)  # Bearish body
        )
        
        # Pin Bar patterns
        patterns['pinbar_bullish'] = (
            (lower_shadow > body_size * 3) &  # Very long lower shadow
            (upper_shadow < body_size * 0.5) &  # Very short upper shadow
            (close > open_price)  # Bullish body
        )
        
        patterns['pinbar_bearish'] = (
            (upper_shadow > body_size * 3) &  # Very long upper shadow
            (lower_shadow < body_size * 0.5) &  # Very short lower shadow
            (close < open_price)  # Bearish body
        )
        
        # Engulfing patterns
        patterns['bullish_engulfing'] = (
            (close > open_price) &  # Current candle is bullish
            (close > high.shift(1)) &  # Current close above previous high
            (open_price < low.shift(1)) &  # Current open below previous low
            (close.shift(1) < open_price.shift(1))  # Previous candle is bearish
        )
        
        patterns['bearish_engulfing'] = (
            (close < open_price) &  # Current candle is bearish
            (open_price > high.shift(1)) &  # Current open above previous high
            (close < low.shift(1)) &  # Current close below previous low
            (close.shift(1) > open_price.shift(1))  # Previous candle is bullish
        )
        
        # Morning Star and Evening Star
        patterns['morning_star'] = (
            (close.shift(2) < open_price.shift(2)) &  # First candle bearish
            (body_size.shift(1) < body_size.shift(2) * 0.5) &  # Second candle small
            (close > open_price) &  # Third candle bullish
            (close > (open_price.shift(2) + close.shift(2)) / 2)  # Third close above midpoint
        )
        
        patterns['evening_star'] = (
            (close.shift(2) > open_price.shift(2)) &  # First candle bullish
            (body_size.shift(1) < body_size.shift(2) * 0.5) &  # Second candle small
            (close < open_price) &  # Third candle bearish
            (close < (open_price.shift(2) + close.shift(2)) / 2)  # Third close below midpoint
        )
        
        # Three White Soldiers and Three Black Crows
        patterns['three_white_soldiers'] = (
            (close > open_price) &  # Current candle bullish
            (close.shift(1) > open_price.shift(1)) &  # Previous candle bullish
            (close.shift(2) > open_price.shift(2)) &  # Two candles ago bullish
            (close > close.shift(1)) &  # Current close higher than previous
            (close.shift(1) > close.shift(2)) &  # Previous close higher than two ago
            (open_price > open_price.shift(1)) &  # Current open higher than previous
            (open_price.shift(1) > open_price.shift(2))  # Previous open higher than two ago
        )
        
        patterns['three_black_crows'] = (
            (close < open_price) &  # Current candle bearish
            (close.shift(1) < open_price.shift(1)) &  # Previous candle bearish
            (close.shift(2) < open_price.shift(2)) &  # Two candles ago bearish
            (close < close.shift(1)) &  # Current close lower than previous
            (close.shift(1) < close.shift(2)) &  # Previous close lower than two ago
            (open_price < open_price.shift(1)) &  # Current open lower than previous
            (open_price.shift(1) < open_price.shift(2))  # Previous open lower than two ago
        )
        
        # Tweezer patterns
        patterns['tweezer_top'] = (
            (high == high.shift(1)) &  # Same high
            (close < open_price) &  # Current candle bearish
            (close.shift(1) > open_price.shift(1))  # Previous candle bullish
        )
        
        patterns['tweezer_bottom'] = (
            (low == low.shift(1)) &  # Same low
            (close > open_price) &  # Current candle bullish
            (close.shift(1) < open_price.shift(1))  # Previous candle bearish
        )
        
        return patterns
