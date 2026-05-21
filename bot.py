import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from FinMind.data import DataLoader
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FINMIND_TOKEN = os.getenv("FINMIND_TOKEN")

dl = DataLoader()
if FINMIND_TOKEN:
    dl.login_by_token(api_token=FINMIND_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍎 阿智水果 FinMind 台股 Bot 已上線！\n\n"
        "直接輸入股票代碼查詢，例如：\n"
        "2330\n"
        "2317\n"
        "2454\n"
        "1101"
    )

async def get_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock_id = update.message.text.strip().upper()
    try:
        # 取得最近資料
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = dl.taiwan_stock_daily(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            await update.message.reply_text(f"⚠️ 找不到 {stock_id} 的資料，請確認股票代碼正確。")
            return
            
        latest = df.iloc[-1]
        change = latest['close'] - latest['open']
        change_pct = (change / latest['open']) * 100 if latest['open'] != 0 else 0
        
        await update.message.reply_text(
            f"📊 **{stock_id}** 最新資訊\n\n"
            f"📅 日期：{latest['date']}\n"
            f"💰 收盤價：**{latest['close']:.2f}**\n"
            f"📈 開盤：{latest['open']:.2f}   最高：{latest['max']:.2f}\n"
            f"📉 最低：{latest['min']:.2f}   成交量：{latest['Trading_Volume']/1000:.0f}張\n"
            f"🔄 漲跌：{change:+.2f}（{change_pct:+.2f}%）"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 查詢失敗：{str(e)[:80]}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_stock))
    
    print("🤖 Bot 開始運行...")
    app.run_polling()

if __name__ == "__main__":
    main()