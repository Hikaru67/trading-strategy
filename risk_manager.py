import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_pnl = 0
        self.open_trades = []
        self.daily_trades = []
        self.reset_daily_stats()
    
    def reset_daily_stats(self):
        """Reset daily statistics at the start of a new day"""
        self.daily_pnl = 0
        self.daily_trades = []
    
    def calculate_position_size(self, account_balance, entry_price, stop_loss_price, risk_percentage=None):
        """
        Calculate position size based on risk management rules
        
        Args:
            account_balance: Current account balance
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price
            risk_percentage: Risk percentage (default from config)
        
        Returns:
            position_size: Calculated position size in base currency
        """
        if risk_percentage is None:
            risk_percentage = self.config.MAX_RISK_PER_TRADE
        
        # Calculate risk amount
        risk_amount = account_balance * risk_percentage
        
        # Calculate price difference
        price_diff = abs(entry_price - stop_loss_price)
        
        if price_diff == 0:
            return 0
        
        # Calculate position size
        position_size = risk_amount / price_diff
        
        # Apply position size limits
        max_position_value = account_balance * self.config.MAX_POSITION_SIZE
        max_position_size = max_position_value / entry_price
        
        position_size = min(position_size, max_position_size)
        
        return position_size
    
    def check_daily_risk_limit(self, new_trade_risk):
        """
        Check if adding a new trade would exceed daily risk limit
        
        Args:
            new_trade_risk: Risk amount of the new trade
        
        Returns:
            bool: True if trade is allowed, False otherwise
        """
        current_daily_risk = sum([trade['risk_amount'] for trade in self.daily_trades])
        total_risk = current_daily_risk + new_trade_risk
        
        return total_risk <= (self.config.MAX_DAILY_RISK * 100)  # Convert to percentage
    
    def check_open_trades_limit(self):
        """
        Check if we can open more trades
        
        Returns:
            bool: True if we can open more trades, False otherwise
        """
        return len(self.open_trades) < self.config.MAX_OPEN_TRADES
    
    def is_trading_hours(self):
        """
        Check if current time is within trading hours
        
        Returns:
            bool: True if within trading hours, False otherwise
        """
        # Get current time in Vietnam timezone
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(vn_tz)
        
        # Check if it's weekend
        if self.config.TRADING_HOURS['avoid_weekends'] and current_time.weekday() >= 5:
            return False
        
        # Check trading hours
        current_hour = current_time.hour
        for start_hour, end_hour in self.config.TRADING_HOURS['active_hours']:
            if start_hour <= current_hour < end_hour:
                return True
        
        return False
    
    def check_market_conditions(self, market_data):
        """
        Check if market conditions are suitable for trading
        
        Args:
            market_data: DataFrame with OHLCV data
        
        Returns:
            dict: Market condition analysis
        """
        if market_data.empty or len(market_data) < 20:
            return {'suitable': False, 'reason': 'Insufficient data'}
        
        # Calculate ATR
        atr = market_data['atr'].iloc[-1] if 'atr' in market_data.columns else None
        if atr is None:
            # Calculate ATR if not provided
            high = market_data['high']
            low = market_data['low']
            close = market_data['close']
            atr = self._calculate_atr(high, low, close).iloc[-1]
        
        # Calculate ATR percentage
        current_price = market_data['close'].iloc[-1]
        atr_percentage = atr / current_price
        
        # Check volatility
        if atr_percentage < self.config.MIN_ATR_PERCENTAGE:
            return {
                'suitable': False, 
                'reason': f'Low volatility: ATR {atr_percentage:.4f} < {self.config.MIN_ATR_PERCENTAGE}'
            }
        
        # Check spread (if bid/ask data available)
        if 'bid' in market_data.columns and 'ask' in market_data.columns:
            spread = (market_data['ask'].iloc[-1] - market_data['bid'].iloc[-1]) / current_price
            if spread > self.config.MAX_SPREAD_PERCENTAGE:
                return {
                    'suitable': False,
                    'reason': f'High spread: {spread:.4f} > {self.config.MAX_SPREAD_PERCENTAGE}'
                }
        
        return {'suitable': True, 'reason': 'Market conditions suitable'}
    
    def _calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def add_trade(self, trade_info):
        """
        Add a new trade to tracking
        
        Args:
            trade_info: Dictionary with trade information
        """
        self.open_trades.append(trade_info)
        self.daily_trades.append(trade_info)
    
    def close_trade(self, trade_id, pnl):
        """
        Close a trade and update statistics
        
        Args:
            trade_id: ID of the trade to close
            pnl: Profit/Loss of the trade
        """
        # Remove from open trades
        self.open_trades = [trade for trade in self.open_trades if trade['id'] != trade_id]
        
        # Update daily PnL
        self.daily_pnl += pnl
    
    def get_risk_summary(self):
        """
        Get current risk management summary
        
        Returns:
            dict: Risk summary
        """
        return {
            'daily_pnl': self.daily_pnl,
            'open_trades_count': len(self.open_trades),
            'daily_trades_count': len(self.daily_trades),
            'max_open_trades': self.config.MAX_OPEN_TRADES,
            'daily_risk_used': sum([trade['risk_amount'] for trade in self.daily_trades]),
            'max_daily_risk': self.config.MAX_DAILY_RISK * 100,
            'trading_hours': self.is_trading_hours()
        }
