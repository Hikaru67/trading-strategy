import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from indicators import TechnicalIndicators
from config import TradingConfig

class DataFetcher:
    def __init__(self, exchange=None, config=None):
        self.config = config or TradingConfig()
        
        if exchange:
            self.exchange = exchange
        else:
            self.exchange = ccxt.binance({
                'enableRateLimit': True,
                'sandbox': False  # Set to True for testing
            })
        
        self.indicators = TechnicalIndicators()
    
    def get_ohlcv(self, symbol, timeframe, limit=100, since=None):
        """
        Fetch OHLCV data from exchange
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '5m', '1h')
            limit: Number of candles to fetch
            since: Start timestamp in milliseconds (optional)
        
        Returns:
            DataFrame: OHLCV data with calculated indicators
        """
        try:
            # Fetch raw OHLCV data
            if since:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            else:
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
    
    def get_ohlcv_from_date(self, symbol, timeframe, start_date, end_date=None):
        """
        Fetch OHLCV data from a specific start date
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '5m', '1h')
            start_date: Start date (datetime)
            end_date: End date (datetime, optional)
        
        Returns:
            DataFrame: OHLCV data with calculated indicators
        """
        try:
            # Calculate timeframe minutes
            if timeframe == '1m':
                minutes = 1
            elif timeframe == '5m':
                minutes = 5
            elif timeframe == '15m':
                minutes = 15
            elif timeframe == '30m':
                minutes = 30
            elif timeframe == '1h':
                minutes = 60
            elif timeframe == '2h':
                minutes = 120
            elif timeframe == '4h':
                minutes = 240
            elif timeframe == '1d':
                minutes = 1440
            else:
                minutes = 60
            
            # If no end_date, just get 1000 candles from start
            if not end_date:
                since = int(start_date.timestamp() * 1000)
                return self.get_ohlcv(symbol, timeframe, limit=1000, since=since)
            
            # Calculate required candles
            total_minutes = int((end_date - start_date).total_seconds() / 60)
            required_candles = total_minutes // minutes
            
            # If we need more than 1000 candles, fetch in chunks
            if required_candles > 1000:
                print(f"Fetching {required_candles} candles in chunks...")
                chunks = []
                current_start = start_date
                
                while current_start < end_date:
                    # Calculate how many candles this chunk should cover
                    remaining_time = end_date - current_start
                    remaining_minutes = int(remaining_time.total_seconds() / 60)
                    remaining_candles = remaining_minutes // minutes
                    
                    # Limit to 1000 candles per chunk
                    chunk_limit = min(remaining_candles + 50, 1000)  # Add buffer
                    
                    # Fetch chunk
                    since = int(current_start.timestamp() * 1000)
                    chunk_df = self.get_ohlcv(symbol, timeframe, limit=chunk_limit, since=since)
                    
                    if chunk_df.empty:
                        break
                    
                    chunks.append(chunk_df)
                    
                    # Move to the next chunk (last timestamp + 1 timeframe)
                    last_timestamp = chunk_df.index[-1]
                    current_start = last_timestamp + timedelta(minutes=minutes)
                    
                    print(f"Fetched chunk: {chunk_df.index[0]} to {chunk_df.index[-1]} ({len(chunk_df)} candles)")
                    
                    # If this chunk covers beyond our end_date, we're done
                    if last_timestamp >= end_date:
                        break
                
                # Combine all chunks
                if chunks:
                    df = pd.concat(chunks).drop_duplicates()
                    df = df.sort_index()
                    print(f"Combined {len(chunks)} chunks into {len(df)} total candles")
                else:
                    df = pd.DataFrame()
            else:
                # Single fetch for shorter periods
                since = int(start_date.timestamp() * 1000)
                df = self.get_ohlcv(symbol, timeframe, limit=required_candles + 100, since=since)
            
            # Filter to end_date if specified
            if end_date and not df.empty:
                df = df[df.index <= end_date]
            
            return df
            
        except Exception as e:
            print(f"Error fetching data from date: {e}")
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
