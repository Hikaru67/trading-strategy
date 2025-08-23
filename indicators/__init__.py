"""
Indicators Package
Technical indicators for trading strategies
"""

from .indicators_basic import BasicIndicators
from .indicators_advanced import AdvancedIndicators
from .indicators_patterns import CandlestickPatterns

class TechnicalIndicators(BasicIndicators, AdvancedIndicators, CandlestickPatterns):
    """
    Combined Technical Indicators class
    Inherits from all indicator modules for backward compatibility
    """
    
    def __init__(self):
        # Initialize all parent classes
        BasicIndicators.__init__(self)
        AdvancedIndicators.__init__(self)
        CandlestickPatterns.__init__(self)
    
    # Add any additional methods that might be needed for compatibility
    def calculate_divergence(self, price, indicator, period=10):
        """
        Legacy method for backward compatibility
        Uses the advanced divergence detection
        """
        return self.calculate_divergence_advanced(price, indicator, period, 100, 10)
    
    def calculate_divergence_peak_detection(self, price, indicator, period=5):
        """
        Legacy method for backward compatibility
        Uses the advanced divergence detection
        """
        return self.calculate_divergence_advanced(price, indicator, period, 100, 10)

__all__ = ['TechnicalIndicators', 'BasicIndicators', 'AdvancedIndicators', 'CandlestickPatterns']
