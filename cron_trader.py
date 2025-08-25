#!/usr/bin/env python3
"""
Cron Trading System
Runs real-time trading every 5 minutes
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime
from real_time_trader import RealTimeTrader

def setup_logging():
    """Setup logging for cron system"""
    log_dir = 'real_time_data'
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/cron_trading.log"),
            logging.StreamHandler()
        ]
    )

def run_trading_job():
    """Run the trading job"""
    try:
        logging.info("🔄 Starting scheduled trading job...")
        
        # Initialize trader with no fees
        trader = RealTimeTrader(
            symbol='SUIUSDT',
            initial_balance=1000,
            strategy_name='ultra_simple_strategy',
            no_fees=True
        )
        
        # Run trading cycle
        trader.run_trading_cycle()
        
        # Get summary
        summary = trader.get_trading_summary()
        
        # Log summary
        logging.info(f"📊 Trading Summary:")
        logging.info(f"   Balance: ${summary['current_balance']:.2f}")
        logging.info(f"   Savings: ${summary['savings_account']:.2f}")
        logging.info(f"   Total Wealth: ${summary['total_wealth']:.2f}")
        logging.info(f"   Return: {summary['total_return']:.2f}%")
        logging.info(f"   Trades: {summary['total_trades']}")
        logging.info(f"   Win Rate: {summary['win_rate']:.1f}%")
        logging.info(f"   Position: {'Open' if summary['open_position'] else 'None'}")
        
        logging.info("✅ Trading job completed successfully")
        
    except Exception as e:
        logging.error(f"❌ Error in trading job: {e}")

def print_status():
    """Print current trading status"""
    try:
        trader = RealTimeTrader(
            symbol='SUIUSDT',
            initial_balance=1000,
            strategy_name='ultra_simple_strategy',
            no_fees=True
        )
        
        summary = trader.get_trading_summary()
        
        print("\n" + "="*60)
        print("🤖 REAL-TIME TRADING SYSTEM STATUS")
        print("="*60)
        print(f"📅 Last Updated: {summary['last_updated']}")
        print(f"💰 Initial Balance: ${summary['initial_balance']:.2f}")
        print(f"💵 Current Balance: ${summary['current_balance']:.2f}")
        print(f"🏦 Savings Account: ${summary['savings_account']:.2f}")
        print(f"💎 Total Wealth: ${summary['total_wealth']:.2f}")
        print(f"📈 Total Return: {summary['total_return']:.2f}%")
        print(f"📊 Total Trades: {summary['total_trades']}")
        print(f"🎯 Win Rate: {summary['win_rate']:.1f}%")
        print(f"📋 Open Position: {'Yes' if summary['open_position'] else 'No'}")
        
        if summary['open_position']:
            position = trader.open_position
            print(f"   └─ {position['side'].upper()} at ${position['entry_price']:.4f}")
            print(f"      SL: ${position['stop_loss']:.4f}, TP: ${position['take_profit']:.4f}")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def main():
    """Main function"""
    setup_logging()
    
    print("🤖 Starting Real-Time Trading System...")
    print("📅 Trading will run at minute 0, 5, 10, 15... (M5 candle close)")
    print("🛑 Press Ctrl+C to stop")
    
    # Schedule trading job at specific minutes (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55)
    schedule.every().hour.at(":00").do(run_trading_job)
    schedule.every().hour.at(":05").do(run_trading_job)
    schedule.every().hour.at(":10").do(run_trading_job)
    schedule.every().hour.at(":15").do(run_trading_job)
    schedule.every().hour.at(":20").do(run_trading_job)
    schedule.every().hour.at(":25").do(run_trading_job)
    schedule.every().hour.at(":30").do(run_trading_job)
    schedule.every().hour.at(":35").do(run_trading_job)
    schedule.every().hour.at(":40").do(run_trading_job)
    schedule.every().hour.at(":45").do(run_trading_job)
    schedule.every().hour.at(":50").do(run_trading_job)
    schedule.every().hour.at(":55").do(run_trading_job)
    
    # Calculate next run time
    now = datetime.now()
    current_minute = now.minute
    next_minute = ((current_minute // 5) + 1) * 5
    if next_minute >= 60:
        next_minute = 0
        next_hour = now.hour + 1
    else:
        next_hour = now.hour
    
    next_run_time = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)
    time_until_next = (next_run_time - now).total_seconds()
    
    print(f"⏰ Next run at: {next_run_time.strftime('%H:%M:%S')}")
    print(f"⏳ Waiting {time_until_next:.0f} seconds...")
    
    # Run initial job if we're at the right minute
    if current_minute % 5 == 0:
        print("🚀 Running initial job (current minute is aligned with M5)")
        run_trading_job()
    else:
        print("⏸️  Skipping initial job (waiting for next M5 alignment)")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)  # Check every 10 seconds for more precise timing
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping trading system...")
        print_status()
        print("👋 Goodbye!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print_status()
    else:
        main()
