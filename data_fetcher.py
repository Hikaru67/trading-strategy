import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from indicators import TechnicalIndicators

class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.exchange = ccxt.binance({
            'apiKey': config.API_KEY,
            'secret': config.API_SECRET,
            'sandbox': False,  # Set to True for testing
            'enableRateLimit': True
        })
        self.indicators = TechnicalIndicators()
    
    def get_ohlcv(self, symbol, timeframe, limit=100):
        """
        Fetch OHLCV data from exchange
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '5m', '1h')
            limit: Number of candles to fetch
        
        Returns:
            DataFrame: OHLCV data with calculated indicators
        """
        try:
            # Fetch raw OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Calculate additional indicators
            df = self._add_indicators(df)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_1h_data(self, symbol, limit=500):
        """
        Get 1H data specifically for high win rate strategy
        
        Args:
            symbol: Trading symbol
            limit: Number of 1H candles to fetch
        
        Returns:
            DataFrame: 1H OHLCV data with indicators
        """
        return self.get_ohlcv(symbol, '1h', limit)
    
    def _add_indicators(self, df):
        """
        Add technical indicators to the DataFrame
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame: Data with indicators added
        """
        if df.empty:
            return df
        
        # Calculate ATR
        df['atr'] = self.indicators.calculate_atr(df['high'], df['low'], df['close'])
        
        # Calculate EMA
        df['ema_20'] = self.indicators.calculate_ema(df['close'], 20)
        df['ema_50'] = self.indicators.calculate_ema(df['close'], 50)
        
        # Calculate RSI
        df['rsi'] = self.indicators.calculate_rsi(df['close'])
        
        # Calculate Bollinger Bands
        bb = self.indicators.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']
        
        # Calculate Stochastic
        stoch = self.indicators.calculate_stochastic(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch['k']
        df['stoch_d'] = stoch['d']
        
        # Calculate MACD
        macd = self.indicators.calculate_macd(df['close'])
        df['macd'] = macd['macd']
        df['macd_signal'] = macd['signal']
        df['macd_histogram'] = macd['histogram']
        
        # Calculate VWAP
        df['vwap'] = self.indicators.calculate_vwap(df['high'], df['low'], df['close'], df['volume'])
        
        # Calculate Ichimoku
        ichimoku = self.indicators.calculate_ichimoku(df['high'], df['low'], df['close'])
        df['tenkan_sen'] = ichimoku['tenkan_sen']
        df['kijun_sen'] = ichimoku['kijun_sen']
        df['senkou_span_a'] = ichimoku['senkou_span_a']
        df['senkou_span_b'] = ichimoku['senkou_span_b']
        df['chikou_span'] = ichimoku['chikou_span']
        
        # Calculate OBV
        df['obv'] = self.indicators.calculate_obv(df['close'], df['volume'])
        
        # Calculate VSA signals
        vsa_signals = self.indicators.calculate_vsa_signals(
            df['open'], df['high'], df['low'], df['close'], df['volume']
        )
        df = pd.concat([df, vsa_signals], axis=1)
        
        return df
    
    def get_current_price(self, symbol):
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            float: Current price
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return None
    
    def get_account_balance(self):
        """
        Get account balance
        
        Returns:
            dict: Account balance information
        """
        try:
            balance = self.exchange.fetch_balance()
            return {
                'total': balance['total'],
                'free': balance['free'],
                'used': balance['used']
            }
        except Exception as e:
            print(f"Error fetching account balance: {e}")
            return {}
    
    def get_order_book(self, symbol, limit=10):
        """
        Get order book for a symbol
        
        Args:
            symbol: Trading symbol
            limit: Number of orders to fetch
        
        Returns:
            dict: Order book data
        """
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return {}
    
    def get_recent_trades(self, symbol, limit=50):
        """
        Get recent trades for a symbol
        
        Args:
            symbol: Trading symbol
            limit: Number of trades to fetch
        
        Returns:
            list: Recent trades
        """
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            return trades
        except Exception as e:
            print(f"Error fetching recent trades: {e}")
            return []
    
    def get_market_data_summary(self, symbol):
        """
        Get comprehensive market data summary
        
        Args:
            symbol: Trading symbol
        
        Returns:
            dict: Market data summary
        """
        try:
            # Get current price
            current_price = self.get_current_price(symbol)
            
            # Get order book
            order_book = self.get_order_book(symbol, 5)
            
            # Get recent trades
            recent_trades = self.get_recent_trades(symbol, 10)
            
            # Calculate spread
            spread = None
            if order_book and 'bids' in order_book and 'asks' in order_book:
                best_bid = order_book['bids'][0][0] if order_book['bids'] else None
                best_ask = order_book['asks'][0][0] if order_book['asks'] else None
                if best_bid and best_ask:
                    spread = (best_ask - best_bid) / current_price
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'best_bid': order_book['bids'][0][0] if order_book and 'bids' in order_book and order_book['bids'] else None,
                'best_ask': order_book['asks'][0][0] if order_book and 'asks' in order_book and order_book['asks'] else None,
                'spread': spread,
                'volume_24h': order_book.get('info', {}).get('volume', 0),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error getting market data summary: {e}")
            return {}
