#!/usr/bin/env python3
"""
Data Cache System for Candle Data
"""

import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

class DataCache:
    """Cache system for storing and retrieving candle data"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        self.logger = logging.getLogger(__name__)
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_key(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> str:
        """Generate cache key for data"""
        start_str = start_date.strftime('%Y%m%d_%H%M%S')
        end_str = end_date.strftime('%Y%m%d_%H%M%S')
        return f"{symbol}_{timeframe}_{start_str}_{end_str}.pkl"
    
    def get_cache_path(self, cache_key: str) -> str:
        """Get full path for cache file"""
        return os.path.join(self.cache_dir, cache_key)
    
    def is_cache_valid(self, cache_path: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        if not os.path.exists(cache_path):
            return False
        
        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_time
        
        return age.total_seconds() < (max_age_hours * 3600)
    
    def save_data(self, symbol: str, timeframe: str, start_date: datetime, 
                  end_date: datetime, data: pd.DataFrame) -> bool:
        """Save data to cache"""
        try:
            cache_key = self.get_cache_key(symbol, timeframe, start_date, end_date)
            cache_path = self.get_cache_path(cache_key)
            
            # Save data with metadata
            cache_data = {
                'symbol': symbol,
                'timeframe': timeframe,
                'start_date': start_date,
                'end_date': end_date,
                'cached_at': datetime.now(),
                'data': data
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.logger.info(f"Data cached: {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")
            return False
    
    def load_data(self, symbol: str, timeframe: str, start_date: datetime, 
                  end_date: datetime, max_age_hours: int = 24) -> Optional[pd.DataFrame]:
        """Load data from cache if valid"""
        try:
            cache_key = self.get_cache_key(symbol, timeframe, start_date, end_date)
            cache_path = self.get_cache_path(cache_key)
            
            if not self.is_cache_valid(cache_path, max_age_hours):
                return None
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Verify data matches request
            if (cache_data['symbol'] == symbol and 
                cache_data['timeframe'] == timeframe and
                cache_data['start_date'] == start_date and
                cache_data['end_date'] == end_date):
                
                self.logger.info(f"Data loaded from cache: {cache_key}")
                return cache_data['data']
            else:
                self.logger.warning(f"Cache data mismatch: {cache_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")
            return None
    
    def clear_old_cache(self, max_age_days: int = 7):
        """Clear old cache files"""
        try:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cleared_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        cleared_count += 1
            
            if cleared_count > 0:
                self.logger.info(f"Cleared {cleared_count} old cache files")
                
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_info(self) -> Dict:
        """Get cache information"""
        try:
            total_files = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    total_size += os.path.getsize(file_path)
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cache info: {e}")
            return {}

class CachedDataFetcher:
    """Data fetcher with caching capabilities"""
    
    def __init__(self, data_fetcher, cache_dir: str = "cache"):
        self.data_fetcher = data_fetcher
        self.cache = DataCache(cache_dir)
        self.logger = logging.getLogger(__name__)
    
    def get_ohlcv_cached(self, symbol: str, timeframe: str, 
                        start_date: datetime, end_date: datetime,
                        max_age_hours: int = 24) -> pd.DataFrame:
        """Get OHLCV data with caching"""
        
        # Try to load from cache first
        cached_data = self.cache.load_data(symbol, timeframe, start_date, end_date, max_age_hours)
        
        if cached_data is not None:
            self.logger.info(f"Using cached data for {symbol} {timeframe}")
            return cached_data
        
        # If not in cache, fetch from API
        self.logger.info(f"Fetching fresh data for {symbol} {timeframe}")
        
        try:
            # Calculate number of candles needed
            if timeframe == '1m':
                minutes = 1
            elif timeframe == '3m':
                minutes = 3
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
                minutes = 5  # default
            
            # Calculate total minutes between start and end
            total_minutes = int((end_date - start_date).total_seconds() / 60)
            required_candles = total_minutes // minutes + 100  # Add buffer
            
            # Use the new method to fetch data from specific start date
            data = self.data_fetcher.get_ohlcv_from_date(symbol, timeframe, start_date, end_date)
            
            if data.empty:
                self.logger.warning(f"No data fetched for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Filter data to requested date range
            data = data[(data.index >= start_date) & (data.index <= end_date)]
            
            # Cache the data
            if not data.empty:
                self.cache.save_data(symbol, timeframe, start_date, end_date, data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_1h_data_cached(self, symbol: str, start_date: datetime, 
                          end_date: datetime, max_age_hours: int = 24) -> pd.DataFrame:
        """Get 1H data with caching"""
        return self.get_ohlcv_cached(symbol, '1h', start_date, end_date, max_age_hours)
    
    def clear_cache(self, max_age_days: int = 7):
        """Clear old cache files"""
        self.cache.clear_old_cache(max_age_days)
    
    def get_cache_info(self) -> Dict:
        """Get cache information"""
        return self.cache.get_cache_info()

# Global cache instance
_global_cache = None

def get_global_cache(cache_dir: str = "cache") -> DataCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = DataCache(cache_dir)
    return _global_cache

def get_cached_fetcher(data_fetcher, cache_dir: str = "cache") -> CachedDataFetcher:
    """Get cached data fetcher instance"""
    return CachedDataFetcher(data_fetcher, cache_dir)
