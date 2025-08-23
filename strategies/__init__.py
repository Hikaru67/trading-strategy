"""
Strategies Package
Trading strategies for cryptocurrency
"""

from .strategies_basic import BasicStrategies
from .strategies_divergence import DivergenceStrategies
from .strategies_advanced import AdvancedStrategies

class TradingStrategies(BasicStrategies, DivergenceStrategies, AdvancedStrategies):
    """
    Combined Trading Strategies class
    Inherits from all strategy modules for backward compatibility
    """
    
    def __init__(self, config=None):
        # Initialize all parent classes
        BasicStrategies.__init__(self)
        DivergenceStrategies.__init__(self)
        AdvancedStrategies.__init__(self, config)
    
    # Add any additional methods that might be needed for compatibility
    def get_all_strategies(self):
        """
        Return list of all available strategies
        """
        return [
            'ema_rsi_strategy',
            'bollinger_stochastic_strategy', 
            'macd_vwap_strategy',
            'divergence_strategy',
            'simple_divergence_strategy',
            'ichimoku_strategy',
            'vsa_obv_strategy',
            'multi_indicator_strategy',
            'ema_rsi_ichimoku_strategy',
            'enhanced_strategy_with_candlestick',
            'flexible_strategy',
            'simple_strategy',
            'wyckoff_vsa_strategy',
            'practical_wyckoff_vsa_strategy',
            'simple_test_strategy',
            'ultra_simple_strategy'
        ]
    
    def run_strategy(self, strategy_name, data, timeframe='1h'):
        """
        Run a specific strategy by name
        """
        if strategy_name == 'ema_rsi_strategy':
            return self.ema_rsi_strategy(data, timeframe)
        elif strategy_name == 'bollinger_stochastic_strategy':
            return self.bollinger_stochastic_strategy(data, timeframe)
        elif strategy_name == 'macd_vwap_strategy':
            return self.macd_vwap_strategy(data, timeframe)
        elif strategy_name == 'divergence_strategy':
            return self.divergence_strategy(data, timeframe)
        elif strategy_name == 'simple_divergence_strategy':
            return self.simple_divergence_strategy(data, timeframe)
        elif strategy_name == 'ichimoku_strategy':
            return self.ichimoku_strategy(data, timeframe)
        elif strategy_name == 'vsa_obv_strategy':
            return self.vsa_obv_strategy(data, timeframe)
        elif strategy_name == 'multi_indicator_strategy':
            return self.multi_indicator_strategy(data, timeframe)
        elif strategy_name == 'ema_rsi_ichimoku_strategy':
            return self.ema_rsi_ichimoku_strategy(data, timeframe)
        elif strategy_name == 'enhanced_strategy_with_candlestick':
            return self.enhanced_strategy_with_candlestick(data, timeframe)
        elif strategy_name == 'flexible_strategy':
            return self.flexible_strategy(data, timeframe)
        elif strategy_name == 'simple_strategy':
            return self.simple_strategy(data, timeframe)
        elif strategy_name == 'wyckoff_vsa_strategy':
            return self.wyckoff_vsa_strategy(data, timeframe)
        elif strategy_name == 'practical_wyckoff_vsa_strategy':
            return self.practical_wyckoff_vsa_strategy(data, timeframe)
        elif strategy_name == 'simple_test_strategy':
            return self.simple_test_strategy(data, timeframe)
        elif strategy_name == 'ultra_simple_strategy':
            return self.ultra_simple_strategy(data, timeframe)
        else:
            return {'signal': 'no_signal', 'reason': f'Strategy {strategy_name} not found'}

__all__ = ['TradingStrategies', 'BasicStrategies', 'DivergenceStrategies', 'AdvancedStrategies']
