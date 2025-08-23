# 📊 Hướng dẫn Backtest với Dữ liệu Nến Quá khứ

## 🎯 Tổng quan

Backtest là quá trình kiểm tra hiệu quả của chiến lược trading bằng cách chạy nó trên dữ liệu lịch sử. Hệ thống này sử dụng dữ liệu nến thực từ Binance để đánh giá hiệu suất của 5 chiến lược trading.

## 🚀 Cách chạy Backtest

### 1. **Backtest Interactive (Khuyến nghị)**

```bash
python run_backtest.py
```

**Tính năng:**
- ✅ Giao diện tương tác dễ sử dụng
- ✅ Chọn khoảng thời gian linh hoạt
- ✅ Chọn chiến lược cụ thể
- ✅ Kết quả chi tiết với phân tích
- ✅ Lưu kết quả ra file Excel

**Các bước:**
1. Chọn khoảng thời gian (1 tuần, 1 tháng, 3 tháng, 6 tháng, 1 năm, hoặc tùy chỉnh)
2. Chọn chiến lược (tất cả hoặc từng chiến lược riêng)
3. Nhập số tiền ban đầu
4. Xem kết quả chi tiết
5. Lưu kết quả nếu muốn

### 2. **Quick Backtest**

```bash
python quick_backtest.py
```

**Tính năng:**
- ✅ Chạy nhanh với cấu hình có sẵn
- ✅ So sánh nhiều chiến lược cùng lúc
- ✅ Kết quả tóm tắt

### 3. **Backtest cơ bản**

```bash
python backtest.py
```

**Tính năng:**
- ✅ Backtest mặc định (tháng 1/2024)
- ✅ Kết quả cơ bản

## 📊 Dữ liệu được sử dụng

### **Nguồn dữ liệu:**
- **Exchange:** Binance
- **Symbol:** BTCUSDT
- **Timeframe:** 5 phút (5m)
- **Dữ liệu:** OHLCV (Open, High, Low, Close, Volume)

### **Khoảng thời gian có thể test:**
- ✅ 1 tuần gần đây
- ✅ 1 tháng gần đây
- ✅ 3 tháng gần đây
- ✅ 6 tháng gần đây
- ✅ 1 năm gần đây
- ✅ Khoảng thời gian tùy chỉnh

## 📈 Các chỉ số được tính toán

### **Technical Indicators:**
1. **EMA (20, 50)** - Exponential Moving Average
2. **RSI (14)** - Relative Strength Index
3. **Bollinger Bands (20, 2)** - Bollinger Bands
4. **Stochastic (14, 3, 3)** - Stochastic Oscillator
5. **MACD (12, 26, 9)** - Moving Average Convergence Divergence
6. **VWAP** - Volume Weighted Average Price
7. **Ichimoku Cloud** - Ichimoku Kinko Hyo
8. **OBV** - On Balance Volume
9. **VSA** - Volume Spread Analysis
10. **ATR (14)** - Average True Range

### **Performance Metrics:**
- **Total Return:** Tổng lợi nhuận (%)
- **Win Rate:** Tỷ lệ lệnh thắng (%)
- **Profit Factor:** Hệ số lợi nhuận
- **Max Drawdown:** Mức sụt giảm tối đa (%)
- **Sharpe Ratio:** Tỷ lệ Sharpe
- **Total Trades:** Tổng số lệnh
- **Average PnL:** Lợi nhuận trung bình

## 🎯 Các chiến lược được test

### **1. EMA + RSI Strategy**
- **Điều kiện vào lệnh:**
  - Long: EMA20 > EMA50 + RSI chạm vùng quá bán (30-40) và bật lên
  - Short: EMA20 < EMA50 + RSI chạm vùng quá mua (60-70) và quay đầu
- **TP/SL:** TP 0.5% - 0.8%, SL ngay sau đáy/đỉnh gần nhất

### **2. Bollinger Bands + Stochastic**
- **Điều kiện vào lệnh:**
  - Long: Giá chạm dải dưới Bollinger + Stochastic < 20
  - Short: Giá chạm dải trên Bollinger + Stochastic > 80
- **TP/SL:** TP ở band giữa hoặc band đối diện

### **3. MACD + VWAP**
- **Điều kiện vào lệnh:**
  - Long: Giá trên VWAP + MACD histogram > 0 + MACD line cắt lên Signal
  - Short: Giá dưới VWAP + MACD histogram < 0 + MACD line cắt xuống Signal
- **TP/SL:** TP 0.5% - 1%, SL khi giá đóng dưới/trên VWAP

### **4. Ichimoku Kinko Hyo**
- **Điều kiện vào lệnh:**
  - Long: Giá trên mây, Tenkan cắt lên Kijun, Chikou span trên giá
  - Short: Giá dưới mây, Tenkan cắt xuống Kijun, Chikou span dưới giá
- **TP/SL:** TP nhanh 0.7% - 1.2%, SL khi nến đóng trong mây ngược hướng

### **5. VSA + OBV**
- **Điều kiện vào lệnh:**
  - Long: Nến tăng mạnh volume cao + OBV đang trend lên
  - Short: Nến giảm mạnh volume cao + OBV trend xuống
- **TP/SL:** TP 0.5% - 1%, SL tại recent high/low

## 📋 Ví dụ kết quả Backtest

```
📈 KẾT QUẢ BACKTEST
======================================================================
💰 Số tiền cuối: 10,450.25 USDT
📊 Tổng lợi nhuận: +4.50%
📈 Tổng số lệnh: 45
✅ Lệnh thắng: 28
❌ Lệnh thua: 17
🎯 Tỷ lệ thắng: 62.22%

📊 THỐNG KÊ NÂNG CAO:
💰 Tổng PnL: +450.25 USDT
📊 PnL trung bình: +10.01 USDT
📈 Profit Factor: 1.85
📉 Max Drawdown: 2.15%
📊 Sharpe Ratio: 1.42

📋 PHÂN TÍCH LỆNH:
🏆 Lệnh thắng lớn nhất: +85.50 USDT
   Chiến lược: ichimoku
   Thời gian: 2024-01-15 14:30 -> 2024-01-15 16:45

💥 Lệnh thua lớn nhất: -32.25 USDT
   Chiến lược: bollinger_stochastic
   Thời gian: 2024-01-20 09:15 -> 2024-01-20 10:30

📊 THỐNG KÊ THEO CHIẾN LƯỢC:
   ichimoku: 12 lệnh, +320.50 USDT, 75.0% thắng
   ema_rsi: 15 lệnh, +180.25 USDT, 66.7% thắng
   macd_vwap: 8 lệnh, -25.75 USDT, 50.0% thắng
   bollinger_stochastic: 6 lệnh, -15.25 USDT, 33.3% thắng
   vsa_obv: 4 lệnh, -9.50 USDT, 25.0% thắng
======================================================================
```

## 🔧 Cấu hình Backtest

### **Risk Management:**
- **Position Sizing:** 1-2% risk per trade
- **Daily Risk Limit:** 5% maximum
- **Max Open Trades:** 3 concurrent trades
- **Stop Loss:** Dynamic based on market conditions
- **Take Profit:** Strategy-specific targets

### **Market Filters:**
- **Minimum ATR:** 0.5% volatility
- **Maximum Spread:** 0.1%
- **Trading Hours:** Optimized for high-volume periods
- **Weekend Avoidance:** Yes

## 📁 File kết quả

Kết quả backtest được lưu trong file Excel với 2 sheet:

### **Sheet 1: Summary**
- Thống kê tổng quan
- Performance metrics
- Risk metrics

### **Sheet 2: Trades**
- Chi tiết từng lệnh
- Entry/Exit times
- PnL per trade
- Strategy used

## ⚠️ Lưu ý quan trọng

### **1. Dữ liệu lịch sử:**
- Dữ liệu được lấy từ Binance API
- Có thể có độ trễ hoặc thiếu dữ liệu
- Chỉ test trên dữ liệu có sẵn

### **2. Slippage & Fees:**
- Backtest không tính phí giao dịch
- Không tính slippage
- Kết quả thực tế có thể khác

### **3. Market Conditions:**
- Quá khứ không đảm bảo tương lai
- Market conditions thay đổi
- Cần test trên nhiều thời kỳ khác nhau

### **4. Overfitting:**
- Tránh tối ưu hóa quá mức
- Test trên out-of-sample data
- Validate với forward testing

## 🎯 Best Practices

### **1. Test nhiều thời kỳ:**
- Bull market
- Bear market
- Sideways market
- High volatility periods

### **2. So sánh chiến lược:**
- Test từng chiến lược riêng
- So sánh performance metrics
- Chọn chiến lược phù hợp

### **3. Risk Analysis:**
- Kiểm tra max drawdown
- Đánh giá risk-adjusted returns
- Xem xét consistency

### **4. Validation:**
- Forward testing
- Paper trading
- Small position testing

## 🚀 Bước tiếp theo

Sau khi backtest:

1. **Phân tích kết quả** - Xem xét các metrics quan trọng
2. **Tối ưu hóa** - Điều chỉnh parameters nếu cần
3. **Forward testing** - Test trên dữ liệu mới
4. **Paper trading** - Test với tài khoản demo
5. **Live trading** - Bắt đầu với số tiền nhỏ

---

**Lưu ý:** Backtest chỉ là công cụ đánh giá, không đảm bảo lợi nhuận trong tương lai. Luôn quản lý risk cẩn thận!
