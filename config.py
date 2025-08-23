import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    # API Configuration
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    
    # Trading Parameters
    SYMBOL = 'BTCUSDT'
    TIMEFRAMES = {
        '1m': '1m',
        '3m': '3m', 
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '4h': '4h'
    }
    
    # Risk Management
    MAX_RISK_PER_TRADE = 0.02  # 2% per trade
    MAX_DAILY_RISK = 0.05      # 5% per day
    MAX_OPEN_TRADES = 3
    
    # Position Sizing
    DEFAULT_POSITION_SIZE = 0.01  # 1% of balance
    MAX_POSITION_SIZE = 0.05      # 5% of balance
    
    # Take Profit & Stop Loss - Optimized for 1H timeframe with 1:3 RR
    TP_PERCENTAGES = {
        'scalping': 0.015,  # 1.5% (1:3 RR)
        'swing': 0.03,      # 3% (1:3 RR)
        'trend': 0.045      # 4.5% (1:3 RR)
    }
    
    SL_PERCENTAGES = {
        'scalping': 0.005,  # 0.5%
        'swing': 0.01,      # 1%
        'trend': 0.015      # 1.5%
    }
    
    # Market Filters
    MIN_ATR_PERCENTAGE = 0.005  # 0.5% minimum volatility
    MAX_SPREAD_PERCENTAGE = 0.001  # 0.1% maximum spread
    
    # Trading Hours (Vietnam time)
    TRADING_HOURS = {
        'active_hours': [
            (15, 17),   # 15:00-17:00 VN
            (20, 24),   # 20:00-24:00 VN
            (2, 4)      # 02:00-04:00 VN (US session)
        ],
        'avoid_weekends': True,
        'avoid_news_time': True
    }
    
    # Strategy Parameters - Optimized for 1H timeframe
    STRATEGY_PARAMS = {
        'ema': {
            'fast': 12,      # Faster EMA for 1H
            'slow': 26,      # Slower EMA for 1H
            'rsi_period': 14,
            'rsi_oversold': 25,  # More conservative oversold
            'rsi_overbought': 75  # More conservative overbought
        },
        'bollinger': {
            'period': 20,
            'std_dev': 2.5,  # Wider bands for 1H
            'stoch_period': 14,
            'stoch_oversold': 15,  # More conservative
            'stoch_overbought': 85  # More conservative
        },
        'macd': {
            'fast': 8,       # Faster MACD for 1H
            'slow': 21,      # Slower MACD for 1H
            'signal': 5      # Faster signal
        },
        'ichimoku': {
            'tenkan': 9,
            'kijun': 26,
            'senkou_b': 52
        },
        'volume': {
            'min_volume_multiplier': 1.5,  # Higher volume requirement
            'obv_trend_period': 10         # Shorter OBV trend
        }
    }
