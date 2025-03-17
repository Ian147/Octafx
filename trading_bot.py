import os
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import telebot
from datetime import datetime, timedelta
import time

# Pengaturan Telegram Bot
TELEGRAM_API_KEY = "8011128170:AAEvCJrvMRinnIsInJmqLjzpWguz88tPWVw"
CHAT_ID = "681125756"
bot = telebot.TeleBot(TELEGRAM_API_KEY)

# Pengaturan Trading
SYMBOL = "XAUUSD"
LOT_SIZE = 0.01
TP_PERCENTAGE = 0.05
SL_PERCENTAGE = 0.05
MODEL_PATH = "lstm_model.h5"

# Load Model AI
model = tf.keras.models.load_model(MODEL_PATH)

# Fungsi untuk mengirim notifikasi Telegram
def send_telegram_message(message):
    bot.send_message(CHAT_ID, message)

# Fungsi mengambil data dari MT5
def get_latest_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 70)
    if rates is None or len(rates) == 0:
        return None
    return pd.DataFrame(rates)[["open", "high", "low", "close", "tick_volume"]]

# Fungsi untuk prediksi sinyal AI
def predict_signal():
    df = get_latest_data()
    if df is None or len(df) < 60:
        return "HOLD"

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)
    X_input = np.array([scaled_data[-60:]])
    prediction = model.predict(X_input)
    last_close = df["close"].iloc[-1]

    if prediction > last_close:
        return "BUY"
    elif prediction < last_close:
        return "SELL"
    return "HOLD"

# Fungsi untuk eksekusi order
def execute_order(signal):
    price = mt5.symbol_info_tick(SYMBOL).ask if signal == "BUY" else mt5.symbol_info_tick(SYMBOL).bid
    tp = price * (1 + TP_PERCENTAGE) if signal == "BUY" else price * (1 - TP_PERCENTAGE)
    sl = price * (1 - SL_PERCENTAGE) if signal == "BUY" else price * (1 + SL_PERCENTAGE)

    order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 123456,
        "comment": "AI Trading Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        send_telegram_message(f"✅ {signal} {SYMBOL}\n💰 Harga: {price}\n📊 TP: {tp}\n📉 SL: {sl}")
    else:
        send_telegram_message(f"❌ Gagal eksekusi {signal}")

# Fungsi utama bot
def run_bot():
    mt5.initialize()
    signal = predict_signal()
    
    if signal in ["BUY", "SELL"]:
        execute_order(signal)
    else:
        send_telegram_message("🤖 Tidak ada sinyal valid saat ini.")
    
    mt5.shutdown()

# Fungsi untuk mengecek apakah market libur
def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:  # Sabtu & Minggu (Market libur)
        return False
    return True

# Jalankan bot setiap 15 menit jika market buka
while True:
    if is_market_open():
        run_bot()
        time.sleep(900)  # 15 menit
    else:
        send_telegram_message("📅 Market sedang libur. Mengecek kembali dalam 1 jam.")
        time.sleep(3600)  # 1 jam
