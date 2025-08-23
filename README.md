# BTCUSDT Trading Strategy Bot

A comprehensive automated trading bot implementing 5 different scalping strategies for BTCUSDT with advanced risk management and backtesting capabilities.

## 🚀 Features

### 📊 Trading Strategies
1. **EMA + RSI Strategy** - Trend following with momentum confirmation
2. **Bollinger Bands + Stochastic** - Sideway market scalping
3. **MACD + VWAP** - Trend following with volume confirmation
4. **Ichimoku Kinko Hyo** - All-in-one indicator system
5. **VSA + OBV** - Volume Spread Analysis with On Balance Volume

### 🛡️ Risk Management
- **Position Sizing**: Automatic calculation based on risk percentage
- **Daily Risk Limits**: Maximum 5% daily risk
- **Stop Loss & Take Profit**: Dynamic SL/TP based on market conditions
- **Market Filters**: ATR-based volatility checks
- **Trading Hours**: Optimized for high-volume periods

### 📈 Backtesting
- Historical data analysis
- Performance metrics calculation
- Strategy comparison
- Risk-adjusted returns

## 📋 Requirements

- Python 3.8+
- Binance API access
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd btc-strategy
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp env_example.txt .env
# Edit .env with your Binance API credentials
```

4. **Configure your API keys**
Edit the `.env` file:
```
BINANCE_API_KEY=your_actual_api_key
BINANCE_SECRET_KEY=your_actual_secret_key
```

## 🚀 Usage

### Running the Trading Bot

```bash
python trading_bot.py
```

### Running Backtests

```bash
python backtest.py
```

### Testing Individual Strategies

```python
from strategies import TradingStrategies
from config import TradingConfig

config = TradingConfig()
strategies = TradingStrategies(config)

# Test specific strategy
signal = strategies.ema_rsi_strategy(market_data, '5m')
print(signal)
```

## 📊 Strategy Details

### 1. EMA + RSI Strategy
- **Timeframe**: 1m - 5m
- **Entry**: EMA20 > EMA50 + RSI oversold bounce
- **Exit**: TP 0.5% - 0.8%, SL at recent low/high

### 2. Bollinger Bands + Stochastic
- **Timeframe**: 1m - 3m
- **Entry**: Price at BB bands + Stochastic oversold/overbought
- **Exit**: TP at middle band or opposite band

### 3. MACD + VWAP
- **Timeframe**: 5m - 15m
- **Entry**: Price above/below VWAP + MACD crossover
- **Exit**: TP 0.5% - 1%, SL at VWAP

### 4. Ichimoku Kinko Hyo
- **Timeframe**: 3m - 5m
- **Entry**: Price above/below cloud + Tenkan/Kijun crossover
- **Exit**: TP 0.7% - 1.2%, SL in cloud

### 5. VSA + OBV
- **Timeframe**: 5m
- **Entry**: High volume bars + OBV trend confirmation
- **Exit**: TP 0.5% - 1%, SL at recent high/low

## ⚙️ Configuration

### Risk Management Settings
```python
# In config.py
MAX_RISK_PER_TRADE = 0.02  # 2% per trade
MAX_DAILY_RISK = 0.05      # 5% per day
MAX_OPEN_TRADES = 3        # Maximum concurrent trades
```

### Trading Hours (Vietnam Time)
- 15:00-17:00 VN
- 20:00-24:00 VN  
- 02:00-04:00 VN (US session)

### Market Filters
- Minimum ATR: 0.5%
- Maximum spread: 0.1%
- Avoid weekends: Yes
- Avoid news time: Yes

## 📈 Performance Metrics

The bot tracks:
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Total Return**: Overall performance

## 🔧 Customization

### Adding New Strategies
1. Create new method in `TradingStrategies` class
2. Add strategy parameters to `config.py`
3. Update `get_all_signals()` method

### Modifying Risk Management
1. Edit parameters in `config.py`
2. Modify `RiskManager` class methods
3. Test with backtesting

### Changing Timeframes
1. Update `TIMEFRAMES` in `config.py`
2. Modify strategy methods
3. Adjust data fetching in `DataFetcher`

## ⚠️ Important Notes

### Risk Disclaimer
- This is for educational purposes
- Cryptocurrency trading involves significant risk
- Never invest more than you can afford to lose
- Test thoroughly before live trading

### API Limits
- Binance has rate limits
- Bot includes rate limiting protection
- Monitor API usage

### Testing
- Always test with small amounts first
- Use sandbox mode for initial testing
- Monitor bot performance closely

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check API keys in `.env`
   - Verify internet connection
   - Check Binance API status

2. **No Trading Signals**
   - Check market conditions
   - Verify indicator calculations
   - Review strategy parameters

3. **Performance Issues**
   - Reduce data fetch frequency
   - Optimize indicator calculations
   - Check system resources

## 📝 Logging

The bot creates detailed logs:
- `trading_bot.log`: Main trading activity
- Console output: Real-time status
- Trade history: CSV export available

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

This project is for educational purposes. Use at your own risk.

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review logs for errors
3. Test with backtesting first
4. Start with small amounts

---

**Remember**: Always test thoroughly and start with small amounts when trading with real money!
