#!/usr/bin/env python3
"""
Smart Money Concepts (SMC) Strategy
Dựa trên cách smart money di chuyển trong thị trường
"""

import pandas as pd
import numpy as np
from indicators.indicators_basic import BasicIndicators
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class SMCStrategies:
    def __init__(self):
        self.indicators = BasicIndicators()
    
    def smc_strategy(self, data, timeframe='1h', min_rr=1.5, max_rr=4.0, reverse_signal=False):
        """
        Smart Money Concepts Strategy
        Dựa trên:
        1. Order Blocks (OB)
        2. Fair Value Gaps (FVG)
        3. Liquidity Levels
        4. Market Structure (Higher Highs/Lower Lows)
        5. Breaker Blocks
        
        Args:
            data: OHLCV data
            timeframe: Trading timeframe
            min_rr: Minimum Risk:Reward ratio
            max_rr: Maximum Risk:Reward ratio
            reverse_signal: Nếu True, đánh ngược lại với tín hiệu (TP làm SL, SL làm TP)
        """
        if len(data) < 100:
            return {'signal': 'no_signal', 'reason': 'Insufficient data for SMC analysis'}
        
        # Get current price
        current_price = data['close'].iloc[-1]
        
        # Use multithreading for parallel analysis
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit tasks for parallel execution
            market_structure_future = executor.submit(self._identify_market_structure, data)
            order_blocks_future = executor.submit(self._find_order_blocks, data)
            fvgs_future = executor.submit(self._find_fair_value_gaps, data)
            liquidity_levels_future = executor.submit(self._find_liquidity_levels, data)
            
            # Get results
            market_structure = market_structure_future.result()
            order_blocks = order_blocks_future.result()
            fvgs = fvgs_future.result()
            liquidity_levels = liquidity_levels_future.result()
        
        # Check for SMC signals
        signal = self._check_smc_signals(data, market_structure, order_blocks, fvgs, liquidity_levels)
        
        if signal['signal'] != 'no_signal':
            # Calculate dynamic R:R based on SMC factors
            predicted_rr = self._predict_smc_rr(data, signal['direction'], order_blocks, fvgs, liquidity_levels)
            predicted_rr = max(min_rr, min(max_rr, predicted_rr))
            
            # Update signal with predicted R:R
            signal['indicators']['predicted_rr'] = predicted_rr
            signal['indicators']['smc_method'] = 'smart_money_concepts'
            signal['indicators']['reverse_signal'] = reverse_signal
            
            # Apply reverse signal logic if enabled
            if reverse_signal:
                # Swap signal direction
                if signal['signal'] == 'long':
                    signal['signal'] = 'short'
                    signal['direction'] = 'short'
                else:
                    signal['signal'] = 'long'
                    signal['direction'] = 'long'
                
                # Swap stop loss and take profit
                original_stop_loss = signal['stop_loss']
                original_take_profit = signal['take_profit']
                
                signal['stop_loss'] = original_take_profit
                signal['take_profit'] = original_stop_loss
                
                # Update indicators
                signal['indicators']['original_signal'] = 'long' if signal['signal'] == 'short' else 'short'
                signal['indicators']['signal_reversed'] = True
            else:
                # Calculate take profit based on predicted R:R (normal mode)
                if signal['signal'] == 'long':
                    risk_per_share = signal['entry_price'] - signal['stop_loss']
                    signal['take_profit'] = signal['entry_price'] + (risk_per_share * predicted_rr)
                else:  # short
                    risk_per_share = signal['stop_loss'] - signal['entry_price']
                    signal['take_profit'] = signal['entry_price'] - (risk_per_share * predicted_rr)
        
        return signal
    
    def _identify_market_structure(self, data):
        """
        Identify market structure (Higher Highs, Lower Lows, etc.)
        Optimized with vectorized operations
        """
        if len(data) < 20:
            return {
                'structure': 'undefined',
                'swing_highs': [],
                'swing_lows': [],
                'current_high': None,
                'current_low': None
            }
        
        # Look for recent swing highs and lows
        lookback = 20
        recent_data = data.iloc[-lookback:]
        
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        # Vectorized swing point detection
        swing_highs = []
        swing_lows = []
        
        # Use vectorized operations for swing detection
        for i in range(2, len(highs) - 2):
            # Swing high conditions
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                swing_highs.append((i, highs[i]))
            
            # Swing low conditions
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                swing_lows.append((i, lows[i]))
        
        # Determine market structure
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Check for Higher Highs (HH) and Higher Lows (HL)
            last_2_highs = sorted(swing_highs[-2:], key=lambda x: x[0])
            last_2_lows = sorted(swing_lows[-2:], key=lambda x: x[0])
            
            if last_2_highs[1][1] > last_2_highs[0][1] and last_2_lows[1][1] > last_2_lows[0][1]:
                structure = 'uptrend'  # HH + HL
            elif last_2_highs[1][1] < last_2_highs[0][1] and last_2_lows[1][1] < last_2_lows[0][1]:
                structure = 'downtrend'  # LH + LL
            elif last_2_highs[1][1] > last_2_highs[0][1] and last_2_lows[1][1] < last_2_lows[0][1]:
                structure = 'consolidation'  # HH + LL
            else:
                structure = 'sideways'  # LH + HL
        else:
            structure = 'undefined'
        
        return {
            'structure': structure,
            'swing_highs': swing_highs,
            'swing_lows': swing_lows,
            'current_high': np.max(highs) if len(highs) > 0 else None,
            'current_low': np.min(lows) if len(lows) > 0 else None
        }
    
    def _find_order_blocks(self, data):
        """
        Find Order Blocks (OB) - areas where smart money placed orders
        Optimized with vectorized operations
        """
        if len(data) < 10:
            return []
        
        # Vectorized calculations
        current_close = data['close'].values
        current_open = data['open'].values
        current_high = data['high'].values
        current_low = data['low'].values
        
        # Shift arrays for comparison
        next_close = np.roll(current_close, -1)
        next_open = np.roll(current_open, -1)
        
        order_blocks = []
        
        # Vectorized conditions
        # Bullish Order Block conditions
        bullish_conditions = (
            (current_close < current_open) &  # Bearish candle
            (next_close > next_open) &        # Bullish candle
            (next_close > current_high)       # Break above previous high
        )
        
        # Bearish Order Block conditions
        bearish_conditions = (
            (current_close > current_open) &  # Bullish candle
            (next_close < next_open) &        # Bearish candle
            (next_close < current_low)        # Break below previous low
        )
        
        # Find indices where conditions are met
        bullish_indices = np.where(bullish_conditions)[0]
        bearish_indices = np.where(bearish_conditions)[0]
        
        # Create order blocks for bullish conditions
        for i in bullish_indices:
            if i < len(data) - 1:  # Ensure we have next candle
                ob = {
                    'type': 'bullish',
                    'index': i,
                    'high': current_high[i],
                    'low': current_low[i],
                    'strength': (next_close[i] - current_high[i]) / current_high[i]
                }
                order_blocks.append(ob)
        
        # Create order blocks for bearish conditions
        for i in bearish_indices:
            if i < len(data) - 1:  # Ensure we have next candle
                ob = {
                    'type': 'bearish',
                    'index': i,
                    'high': current_high[i],
                    'low': current_low[i],
                    'strength': (current_low[i] - next_close[i]) / current_low[i]
                }
                order_blocks.append(ob)
        
        return order_blocks
    
    def _find_fair_value_gaps(self, data):
        """
        Find Fair Value Gaps (FVG) - areas where price moved too fast
        Optimized with vectorized operations
        """
        if len(data) < 2:
            return []
        
        # Vectorized calculations
        current_high = data['high'].values
        current_low = data['low'].values
        
        # Shift arrays for comparison
        next_high = np.roll(current_high, -1)
        next_low = np.roll(current_low, -1)
        
        fvgs = []
        
        # Vectorized conditions
        # Bullish FVG conditions (gap up)
        bullish_fvg_conditions = current_high < next_low
        
        # Bearish FVG conditions (gap down)
        bearish_fvg_conditions = current_low > next_high
        
        # Find indices where conditions are met
        bullish_indices = np.where(bullish_fvg_conditions)[0]
        bearish_indices = np.where(bearish_fvg_conditions)[0]
        
        # Create FVGs for bullish conditions
        for i in bullish_indices:
            if i < len(data) - 1:  # Ensure we have next candle
                fvg = {
                    'type': 'bullish',
                    'index': i,
                    'high': current_high[i],
                    'low': next_low[i],
                    'gap_size': (next_low[i] - current_high[i]) / current_high[i]
                }
                fvgs.append(fvg)
        
        # Create FVGs for bearish conditions
        for i in bearish_indices:
            if i < len(data) - 1:  # Ensure we have next candle
                fvg = {
                    'type': 'bearish',
                    'index': i,
                    'high': current_low[i],
                    'low': next_high[i],
                    'gap_size': (current_low[i] - next_high[i]) / current_low[i]
                }
                fvgs.append(fvg)
        
        return fvgs
    
    def _find_liquidity_levels(self, data):
        """
        Find Liquidity Levels - areas where stops are likely to be placed
        Optimized with vectorized operations
        """
        if len(data) < 20:
            return []
        
        lookback = 20
        liquidity_levels = []
        
        # Vectorized calculations
        highs = data['high'].values
        lows = data['low'].values
        volumes = data['volume'].values
        
        # Calculate rolling max/min and mean
        recent_highs = pd.Series(highs).rolling(lookback).max().values
        recent_lows = pd.Series(lows).rolling(lookback).min().values
        volume_sma = pd.Series(volumes).rolling(20).mean().values
        
        # Vectorized conditions for equal highs and lows
        equal_high_conditions = np.abs(highs - recent_highs) < 0.001
        equal_low_conditions = np.abs(lows - recent_lows) < 0.001
        
        # Find indices where conditions are met
        equal_high_indices = np.where(equal_high_conditions)[0]
        equal_low_indices = np.where(equal_low_conditions)[0]
        
        # Create liquidity levels for equal highs
        for i in equal_high_indices:
            if i >= lookback and not np.isnan(volume_sma[i]):
                level = {
                    'type': 'equal_high',
                    'price': highs[i],
                    'index': i,
                    'strength': volumes[i] / volume_sma[i]
                }
                liquidity_levels.append(level)
        
        # Create liquidity levels for equal lows
        for i in equal_low_indices:
            if i >= lookback and not np.isnan(volume_sma[i]):
                level = {
                    'type': 'equal_low',
                    'price': lows[i],
                    'index': i,
                    'strength': volumes[i] / volume_sma[i]
                }
                liquidity_levels.append(level)
        
        return liquidity_levels
    
    def _check_smc_signals(self, data, market_structure, order_blocks, fvgs, liquidity_levels):
        """
        Check for SMC trading signals
        """
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # 1. Order Block Retest Signal
        for ob in order_blocks[-5:]:  # Check recent order blocks
            if ob['type'] == 'bullish' and ob['strength'] > 0.01:
                # Price retesting bullish order block
                if (current_price >= ob['low'] and current_price <= ob['high'] and
                    current_volume > avg_volume * 1.2):
                    
                    return {
                        'signal': 'long',
                        'entry_price': current_price,
                        'stop_loss': ob['low'] * 0.995,  # Below order block
                        'take_profit': current_price * 1.02,  # Temporary
                        'strategy': 'smc_strategy',
                        'confidence': 0.7,
                        'account_risk_percent': 1.0,
                        'direction': 'long',
                        'indicators': {
                            'signal_type': 'order_block_retest',
                            'order_block_strength': ob['strength'],
                            'volume_ratio': current_volume / avg_volume,
                            'market_structure': market_structure['structure']
                        }
                    }
            
            elif ob['type'] == 'bearish' and ob['strength'] > 0.01:
                # Price retesting bearish order block
                if (current_price >= ob['low'] and current_price <= ob['high'] and
                    current_volume > avg_volume * 1.2):
                    
                    return {
                        'signal': 'short',
                        'entry_price': current_price,
                        'stop_loss': ob['high'] * 1.005,  # Above order block
                        'take_profit': current_price * 0.98,  # Temporary
                        'strategy': 'smc_strategy',
                        'confidence': 0.7,
                        'account_risk_percent': 1.0,
                        'direction': 'short',
                        'indicators': {
                            'signal_type': 'order_block_retest',
                            'order_block_strength': ob['strength'],
                            'volume_ratio': current_volume / avg_volume,
                            'market_structure': market_structure['structure']
                        }
                    }
        
        # 2. Fair Value Gap Fill Signal
        for fvg in fvgs[-3:]:  # Check recent FVGs
            if fvg['type'] == 'bullish' and fvg['gap_size'] > 0.005:
                # Price filling bullish FVG
                if (current_price >= fvg['low'] and current_price <= fvg['high'] and
                    current_volume > avg_volume * 1.1):
                    
                    return {
                        'signal': 'long',
                        'entry_price': current_price,
                        'stop_loss': fvg['low'] * 0.995,
                        'take_profit': current_price * 1.02,
                        'strategy': 'smc_strategy',
                        'confidence': 0.6,
                        'account_risk_percent': 1.0,
                        'direction': 'long',
                        'indicators': {
                            'signal_type': 'fvg_fill',
                            'fvg_size': fvg['gap_size'],
                            'volume_ratio': current_volume / avg_volume,
                            'market_structure': market_structure['structure']
                        }
                    }
            
            elif fvg['type'] == 'bearish' and fvg['gap_size'] > 0.005:
                # Price filling bearish FVG
                if (current_price >= fvg['low'] and current_price <= fvg['high'] and
                    current_volume > avg_volume * 1.1):
                    
                    return {
                        'signal': 'short',
                        'entry_price': current_price,
                        'stop_loss': fvg['high'] * 1.005,
                        'take_profit': current_price * 0.98,
                        'strategy': 'smc_strategy',
                        'confidence': 0.6,
                        'account_risk_percent': 1.0,
                        'direction': 'short',
                        'indicators': {
                            'signal_type': 'fvg_fill',
                            'fvg_size': fvg['gap_size'],
                            'volume_ratio': current_volume / avg_volume,
                            'market_structure': market_structure['structure']
                        }
                    }
        
        # 3. Liquidity Grab Signal
        for level in liquidity_levels[-3:]:
            if level['type'] == 'equal_low' and level['strength'] > 1.5:
                # Price grabbing liquidity at equal low
                if (abs(current_price - level['price']) / level['price'] < 0.002 and
                    current_volume > avg_volume * 1.3):
                    
                    return {
                        'signal': 'long',
                        'entry_price': current_price,
                        'stop_loss': level['price'] * 0.995,
                        'take_profit': current_price * 1.02,
                        'strategy': 'smc_strategy',
                        'confidence': 0.8,
                        'account_risk_percent': 1.0,
                        'direction': 'long',
                        'indicators': {
                            'signal_type': 'liquidity_grab',
                            'liquidity_strength': level['strength'],
                            'volume_ratio': current_volume / avg_volume,
                            'market_structure': market_structure['structure']
                        }
                    }
            
            elif level['type'] == 'equal_high' and level['strength'] > 1.5:
                # Price grabbing liquidity at equal high
                if (abs(current_price - level['price']) / level['price'] < 0.002 and
                    current_volume > avg_volume * 1.3):
                    
                    return {
                        'signal': 'short',
                        'entry_price': current_price,
                        'stop_loss': level['price'] * 1.005,
                        'take_profit': current_price * 0.98,
                        'strategy': 'smc_strategy',
                        'confidence': 0.8,
                        'account_risk_percent': 1.0,
                        'direction': 'short',
                        'indicators': {
                            'signal_type': 'liquidity_grab',
                            'liquidity_strength': level['strength'],
                            'volume_ratio': current_volume / avg_volume,
                            'market_structure': market_structure['structure']
                        }
                    }
        
        return {'signal': 'no_signal', 'reason': 'No SMC signal detected'}
    
    def _predict_smc_rr(self, data, direction, order_blocks, fvgs, liquidity_levels):
        """
        Predict R:R ratio based on SMC factors
        """
        base_rr = 2.0
        
        # Factor 1: Order Block Strength
        if order_blocks:
            recent_ob = order_blocks[-1]
            if recent_ob['strength'] > 0.02:
                base_rr += 0.5
            elif recent_ob['strength'] < 0.005:
                base_rr -= 0.3
        
        # Factor 2: FVG Size
        if fvgs:
            recent_fvg = fvgs[-1]
            if recent_fvg['gap_size'] > 0.01:
                base_rr += 0.4
            elif recent_fvg['gap_size'] < 0.002:
                base_rr -= 0.2
        
        # Factor 3: Liquidity Strength
        if liquidity_levels:
            recent_level = liquidity_levels[-1]
            if recent_level['strength'] > 2.0:
                base_rr += 0.6
            elif recent_level['strength'] < 1.0:
                base_rr -= 0.3
        
        # Factor 4: Market Structure
        market_structure = self._identify_market_structure(data)
        if market_structure['structure'] == 'uptrend' and direction == 'long':
            base_rr += 0.3
        elif market_structure['structure'] == 'downtrend' and direction == 'short':
            base_rr += 0.3
        elif market_structure['structure'] == 'sideways':
            base_rr -= 0.2
        
        return max(1.5, min(4.0, base_rr))
    
    def breaker_block_strategy(self, data, timeframe='1h'):
        """
        Breaker Block Strategy - trading breakouts from order blocks
        """
        if len(data) < 50:
            return {'signal': 'no_signal', 'reason': 'Insufficient data'}
        
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        # Find order blocks
        order_blocks = self._find_order_blocks(data)
        
        # Check for breaker block signals
        for ob in order_blocks[-10:]:
            if ob['type'] == 'bullish' and ob['strength'] > 0.01:
                # Price breaking above bullish order block
                if (current_price > ob['high'] and 
                    current_volume > avg_volume * 1.5):
                    
                    return {
                        'signal': 'long',
                        'entry_price': current_price,
                        'stop_loss': ob['low'] * 0.995,
                        'take_profit': current_price + (current_price - ob['low']) * 2,
                        'strategy': 'breaker_block_strategy',
                        'confidence': 0.8,
                        'account_risk_percent': 1.0,
                        'indicators': {
                            'signal_type': 'breaker_block_long',
                            'order_block_strength': ob['strength'],
                            'volume_ratio': current_volume / avg_volume,
                            'breakout_strength': (current_price - ob['high']) / ob['high']
                        }
                    }
            
            elif ob['type'] == 'bearish' and ob['strength'] > 0.01:
                # Price breaking below bearish order block
                if (current_price < ob['low'] and 
                    current_volume > avg_volume * 1.5):
                    
                    return {
                        'signal': 'short',
                        'entry_price': current_price,
                        'stop_loss': ob['high'] * 1.005,
                        'take_profit': current_price - (ob['high'] - current_price) * 2,
                        'strategy': 'breaker_block_strategy',
                        'confidence': 0.8,
                        'account_risk_percent': 1.0,
                        'indicators': {
                            'signal_type': 'breaker_block_short',
                            'order_block_strength': ob['strength'],
                            'volume_ratio': current_volume / avg_volume,
                            'breakout_strength': (ob['low'] - current_price) / ob['low']
                        }
                    }
        
        return {'signal': 'no_signal', 'reason': 'No breaker block signal'}
