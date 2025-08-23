import pandas as pd
import numpy as np
import ta

class AdvancedIndicators:
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
        
        # High volume, narrow spread (accumulation)
        vsa_signals['accumulation'] = (volume > avg_volume * 1.5) & (price_spread < avg_spread * 0.8)
        
        # High volume, wide spread (distribution)
        vsa_signals['distribution'] = (volume > avg_volume * 1.5) & (price_spread > avg_spread * 1.2)
        
        # Low volume, narrow spread (no demand)
        vsa_signals['no_demand'] = (volume < avg_volume * 0.8) & (price_spread < avg_spread * 0.8)
        
        # Low volume, wide spread (no supply)
        vsa_signals['no_supply'] = (volume < avg_volume * 0.8) & (price_spread > avg_spread * 1.2)
        
        return vsa_signals
    
    @staticmethod
    def calculate_divergence_simple(price, indicator, period=10):
        """
        Simple and fast divergence calculation
        Uses rolling min/max instead of complex pivot detection
        """
        if len(price) < period * 2:
            return pd.DataFrame()
        
        # Calculate rolling min/max
        price_rolling_min = price.rolling(window=period, center=True).min()
        price_rolling_max = price.rolling(window=period, center=True).max()
        indicator_rolling_min = indicator.rolling(window=period, center=True).min()
        indicator_rolling_max = indicator.rolling(window=period, center=True).max()
        
        # Initialize divergence DataFrame
        divergence = pd.DataFrame(index=price.index)
        divergence['bullish_divergence'] = False
        divergence['bearish_divergence'] = False
        divergence['hidden_bullish_divergence'] = False
        divergence['hidden_bearish_divergence'] = False
        
        # Simple divergence detection
        for i in range(period, len(price) - period):
            # Regular Bullish Divergence: Price makes lower low, indicator makes higher low
            if (price.iloc[i] < price_rolling_min.iloc[i-1] and 
                indicator.iloc[i] > indicator_rolling_min.iloc[i-1] and
                indicator.iloc[i] > indicator.iloc[i-1]):  # Confirmation
                divergence.loc[price.index[i], 'bullish_divergence'] = True
            
            # Regular Bearish Divergence: Price makes higher high, indicator makes lower high
            elif (price.iloc[i] > price_rolling_max.iloc[i-1] and 
                  indicator.iloc[i] < indicator_rolling_max.iloc[i-1] and
                  indicator.iloc[i] < indicator.iloc[i-1]):  # Confirmation
                divergence.loc[price.index[i], 'bearish_divergence'] = True
            
            # Hidden Bullish Divergence: Price makes higher low, indicator makes lower low
            elif (price.iloc[i] > price_rolling_min.iloc[i-1] and 
                  indicator.iloc[i] < indicator_rolling_min.iloc[i-1] and
                  indicator.iloc[i] < indicator.iloc[i-1]):  # Confirmation
                divergence.loc[price.index[i], 'hidden_bullish_divergence'] = True
            
            # Hidden Bearish Divergence: Price makes lower high, indicator makes higher high
            elif (price.iloc[i] < price_rolling_max.iloc[i-1] and 
                  indicator.iloc[i] > indicator_rolling_max.iloc[i-1] and
                  indicator.iloc[i] > indicator.iloc[i-1]):  # Confirmation
                divergence.loc[price.index[i], 'hidden_bearish_divergence'] = True
        
        return divergence

    @staticmethod
    def calculate_divergence_advanced(price, indicator, min_bars=5, max_bars=100, confirmation_bars=10, period=5, max_pivots=10):
        """
        Advanced divergence detection based on Pine Script logic
        - Uses pivot high/low detection
        - Checks multiple pivot points
        - Validates divergence with slope analysis
        """
        divergence = pd.DataFrame(index=price.index)
        divergence['bullish_divergence'] = False
        divergence['bearish_divergence'] = False
        divergence['hidden_bullish_divergence'] = False
        divergence['hidden_bearish_divergence'] = False
        
        # Detect pivot highs and lows
        pivot_highs = []
        pivot_lows = []
        pivot_high_vals = []
        pivot_low_vals = []
        
        for i in range(period, len(price) - period):
            # Pivot High
            if all(price.iloc[i] >= price.iloc[i-period:i]) and all(price.iloc[i] >= price.iloc[i+1:i+period+1]):
                pivot_highs.append(i)
                pivot_high_vals.append(price.iloc[i])
            
            # Pivot Low
            if all(price.iloc[i] <= price.iloc[i-period:i]) and all(price.iloc[i] <= price.iloc[i+1:i+period+1]):
                pivot_lows.append(i)
                pivot_low_vals.append(price.iloc[i])
        
        # Keep only recent pivots (max_pivots)
        pivot_highs = pivot_highs[-max_pivots:]
        pivot_lows = pivot_lows[-max_pivots:]
        pivot_high_vals = pivot_high_vals[-max_pivots:]
        pivot_low_vals = pivot_low_vals[-max_pivots:]
        
        # Check for divergences at each point
        for i in range(len(price)):
            current_price = price.iloc[i]
            current_indicator = indicator.iloc[i]
            
            # Regular Bullish Divergence: Price makes lower low, indicator makes higher low
            for j, pivot_idx in enumerate(pivot_lows):
                if i - pivot_idx > 5 and i - pivot_idx <= max_bars:
                    pivot_price = pivot_low_vals[j]
                    pivot_indicator = indicator.iloc[pivot_idx]
                    
                    # Check conditions for regular bullish divergence
                    if (current_price < pivot_price and current_indicator > pivot_indicator and
                        current_indicator > indicator.iloc[i-1]):  # Confirmation
                        
                        # Validate with slope analysis
                        if AdvancedIndicators._validate_divergence_slope(
                            price.iloc[pivot_idx:i+1], 
                            indicator.iloc[pivot_idx:i+1], 
                            pivot_idx, i, 'bullish_regular'
                        ):
                            divergence.loc[price.index[i], 'bullish_divergence'] = True
                            break
            
            # Regular Bearish Divergence: Price makes higher high, indicator makes lower high
            for j, pivot_idx in enumerate(pivot_highs):
                if i - pivot_idx > 5 and i - pivot_idx <= max_bars:
                    pivot_price = pivot_high_vals[j]
                    pivot_indicator = indicator.iloc[pivot_idx]
                    
                    # Check conditions for regular bearish divergence
                    if (current_price > pivot_price and current_indicator < pivot_indicator and
                        current_indicator < indicator.iloc[i-1]):  # Confirmation
                        
                        # Validate with slope analysis
                        if AdvancedIndicators._validate_divergence_slope(
                            price.iloc[pivot_idx:i+1], 
                            indicator.iloc[pivot_idx:i+1], 
                            pivot_idx, i, 'bearish_regular'
                        ):
                            divergence.loc[price.index[i], 'bearish_divergence'] = True
                            break
            
            # Hidden Bullish Divergence: Price makes higher low, indicator makes lower low
            for j, pivot_idx in enumerate(pivot_lows):
                if i - pivot_idx > 5 and i - pivot_idx <= max_bars:
                    pivot_price = pivot_low_vals[j]
                    pivot_indicator = indicator.iloc[pivot_idx]
                    
                    # Check conditions for hidden bullish divergence
                    if (current_price > pivot_price and current_indicator < pivot_indicator and
                        current_indicator < indicator.iloc[i-1]):  # Confirmation
                        
                        # Validate with slope analysis
                        if AdvancedIndicators._validate_divergence_slope(
                            price.iloc[pivot_idx:i+1], 
                            indicator.iloc[pivot_idx:i+1], 
                            pivot_idx, i, 'bullish_hidden'
                        ):
                            divergence.loc[price.index[i], 'hidden_bullish_divergence'] = True
                            break
            
            # Hidden Bearish Divergence: Price makes lower high, indicator makes higher high
            for j, pivot_idx in enumerate(pivot_highs):
                if i - pivot_idx > 5 and i - pivot_idx <= max_bars:
                    pivot_price = pivot_high_vals[j]
                    pivot_indicator = indicator.iloc[pivot_idx]
                    
                    # Check conditions for hidden bearish divergence
                    if (current_price < pivot_price and current_indicator > pivot_indicator and
                        current_indicator > indicator.iloc[i-1]):  # Confirmation
                        
                        # Validate with slope analysis
                        if AdvancedIndicators._validate_divergence_slope(
                            price.iloc[pivot_idx:i+1], 
                            indicator.iloc[pivot_idx:i+1], 
                            pivot_idx, i, 'bearish_hidden'
                        ):
                            divergence.loc[price.index[i], 'hidden_bearish_divergence'] = True
                            break
        
        return divergence

    @staticmethod
    def _validate_divergence_slope(price_segment, indicator_segment, start_idx, end_idx, div_type):
        """
        Validate divergence using slope analysis (simplified version)
        """
        if len(price_segment) < 3:
            return False
        
        # Calculate slopes
        price_slope = (price_segment.iloc[-1] - price_segment.iloc[0]) / len(price_segment)
        indicator_slope = (indicator_segment.iloc[-1] - indicator_segment.iloc[0]) / len(indicator_segment)
        
        # Check if slopes are consistent with divergence type
        if div_type in ['bullish_regular', 'bearish_hidden']:
            # Price and indicator should move in opposite directions
            return (price_slope < 0 and indicator_slope > 0) or (price_slope > 0 and indicator_slope < 0)
        elif div_type in ['bearish_regular', 'bullish_hidden']:
            # Price and indicator should move in opposite directions
            return (price_slope > 0 and indicator_slope < 0) or (price_slope < 0 and indicator_slope > 0)
        
        return True

    @staticmethod
    def calculate_volume_divergence(price, volume, period=10):
        """Calculate volume divergence"""
        divergence = pd.DataFrame(index=price.index)
        divergence['bullish_volume_divergence'] = False
        divergence['bearish_volume_divergence'] = False
        
        # Calculate rolling min/max for price and volume
        price_rolling_min = price.rolling(window=period*2+1, center=True).min()
        price_rolling_max = price.rolling(window=period*2+1, center=True).max()
        volume_rolling_min = volume.rolling(window=period*2+1, center=True).min()
        volume_rolling_max = volume.rolling(window=period*2+1, center=True).max()
        
        # Calculate changes
        price_change = price - price.shift(period)
        volume_change = volume - volume.shift(period)
        
        # Bullish volume divergence: price lower low, volume higher low
        bullish_condition = (
            (price == price_rolling_min) &  # Current price is local minimum
            (volume > volume_rolling_min) &  # Volume is above its minimum
            (price_change < 0) &  # Price is lower than period ago
            (volume_change > 0)  # Volume is higher than period ago
        )
        
        # Bearish volume divergence: price higher high, volume lower high
        bearish_condition = (
            (price == price_rolling_max) &  # Current price is local maximum
            (volume < volume_rolling_max) &  # Volume is below its maximum
            (price_change > 0) &  # Price is higher than period ago
            (volume_change < 0)  # Volume is lower than period ago
        )
        
        divergence['bullish_volume_divergence'] = bullish_condition
        divergence['bearish_volume_divergence'] = bearish_condition
        
        return divergence

    @staticmethod
    def calculate_macd_divergence(price, macd_line, period=10):
        """Calculate MACD divergence"""
        divergence = pd.DataFrame(index=price.index)
        divergence['macd_bullish_divergence'] = False
        divergence['macd_bearish_divergence'] = False
        
        # Calculate rolling min/max
        price_rolling_min = price.rolling(window=period*2+1, center=True).min()
        price_rolling_max = price.rolling(window=period*2+1, center=True).max()
        macd_rolling_min = macd_line.rolling(window=period*2+1, center=True).min()
        macd_rolling_max = macd_line.rolling(window=period*2+1, center=True).max()
        
        # Calculate changes
        price_change = price - price.shift(period)
        macd_change = macd_line - macd_line.shift(period)
        
        # Bullish MACD divergence: price lower low, MACD higher low
        bullish_condition = (
            (price == price_rolling_min) &  # Current price is local minimum
            (macd_line > macd_rolling_min) &  # MACD is above its minimum
            (price_change < 0) &  # Price is lower than period ago
            (macd_change > 0)  # MACD is higher than period ago
        )
        
        # Bearish MACD divergence: price higher high, MACD lower high
        bearish_condition = (
            (price == price_rolling_max) &  # Current price is local maximum
            (macd_line < macd_rolling_max) &  # MACD is below its maximum
            (price_change > 0) &  # Price is higher than period ago
            (macd_change < 0)  # MACD is lower than period ago
        )
        
        divergence['macd_bullish_divergence'] = bullish_condition
        divergence['macd_bearish_divergence'] = bearish_condition
        
        return divergence
