# 🤖 Real-Time Trading System

Hệ thống trading thời gian thực sử dụng `ultra_simple_strategy` với SUIUSDT.

## 🚀 Tính năng

- ✅ **Cron job chạy mỗi 5 phút**
- ✅ **Lưu trữ dữ liệu vào JSON files**
- ✅ **Tính năng savings account (10% lợi nhuận)**
- ✅ **Position scaling (x2 khi có lãi)**
- ✅ **Dashboard để theo dõi**
- ✅ **Logging chi tiết**

## 📁 Cấu trúc file

```
real_time_data/
├── balance_SUIUSDT.json      # Balance và savings account
├── trades_SUIUSDT.json       # Lịch sử trades
├── equity_SUIUSDT.json       # Equity curve
├── trading.log               # Log trading
└── cron_trading.log          # Log cron system
```

## 🛠️ Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install -r requirements_realtime.txt
```

2. **Chạy test một lần:**
```bash
python real_time_trader.py
```

3. **Chạy hệ thống cron (mỗi 5 phút):**
```bash
python cron_trader.py
```

## 📊 Sử dụng

### 1. Chạy Trading System
```bash
# Chạy một lần
python real_time_trader.py

# Chạy cron (mỗi 5 phút)
python cron_trader.py

# Xem status
python cron_trader.py status
```

### 2. Xem Dashboard
```bash
# Dashboard chính
python trading_dashboard.py dashboard

# Equity chart
python trading_dashboard.py equity

# Chi tiết trades
python trading_dashboard.py trades

# Tất cả
python trading_dashboard.py all
```

## 📈 Cấu hình

### Trading Parameters
- **Symbol**: SUIUSDT
- **Strategy**: ultra_simple_strategy
- **Timeframe**: 5m
- **Initial Balance**: $1,000
- **Risk per trade**: 1% (1R)
- **Reward Ratio**: 1:1
- **Position Scaling**: x2 khi có lãi
- **Savings**: 10% lợi nhuận

### File Configuration
- **Balance File**: `real_time_data/balance_SUIUSDT.json`
- **Trades File**: `real_time_data/trades_SUIUSDT.json`
- **Equity File**: `real_time_data/equity_SUIUSDT.json`

## 🔄 Workflow

1. **Mỗi 5 phút:**
   - Lấy dữ liệu thị trường (2 giờ gần nhất)
   - Kiểm tra position hiện tại (SL/TP)
   - Tìm tín hiệu mới
   - Mở position mới nếu có tín hiệu
   - Lưu dữ liệu

2. **Position Management:**
   - **Entry**: Khi có tín hiệu LONG/SHORT
   - **Stop Loss**: 1R risk
   - **Take Profit**: 1:1 reward ratio
   - **Scaling**: x2 khi account có lãi

3. **Savings Logic:**
   - 10% lợi nhuận được chuyển vào savings account
   - Chỉ áp dụng khi account có lãi

## 📊 Monitoring

### Dashboard Features
- **Account Balance**: Balance hiện tại, savings, total wealth
- **Trading Performance**: Số trades, win rate, PnL
- **Current Position**: Position đang mở (nếu có)
- **Recent Trades**: 10 trades gần nhất
- **Equity Curve**: Biểu đồ equity

### Log Files
- **trading.log**: Log chi tiết mỗi trading cycle
- **cron_trading.log**: Log cron system

## 🔧 Customization

### Thay đổi Strategy
```python
trader = RealTimeTrader(
    symbol='SUIUSDT',
    initial_balance=1000,
    strategy_name='your_strategy'  # Thay đổi strategy
)
```

### Thay đổi Parameters
```python
# Trong real_time_trader.py
self.scaling_enabled = True
self.scaling_threshold = 1.0      # R:R threshold
self.scaling_multiplier = 2.0     # Scaling multiplier
```

### Thay đổi Symbol
```python
trader = RealTimeTrader(
    symbol='BTCUSDT',  # Thay đổi symbol
    initial_balance=1000,
    strategy_name='ultra_simple_strategy'
)
```

## ⚠️ Lưu ý

1. **Demo System**: Hiện tại sử dụng dữ liệu historical, chưa kết nối API thật
2. **Risk Management**: Hệ thống có risk cao, cần test kỹ trước khi dùng thật
3. **Backup**: Dữ liệu được lưu trong JSON files, cần backup định kỳ
4. **Monitoring**: Theo dõi log files để phát hiện lỗi

## 🔮 Future Features

- [ ] **Real API Integration**: Kết nối Binance API thật
- [ ] **Web Dashboard**: Dashboard web interface
- [ ] **Email Alerts**: Thông báo qua email
- [ ] **Telegram Bot**: Bot Telegram để monitor
- [ ] **Multiple Strategies**: Hỗ trợ nhiều strategies
- [ ] **Backtesting Integration**: Tích hợp với backtesting system

## 📞 Support

Nếu có vấn đề, kiểm tra:
1. Log files trong `real_time_data/`
2. Dữ liệu JSON files
3. Network connection (cho API calls)

---
*Real-Time Trading System v1.0*
