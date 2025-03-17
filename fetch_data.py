import MetaTrader5 as mt5
import pandas as pd

# Inisialisasi MetaTrader 5
if not mt5.initialize():
    print("Gagal menginisialisasi MetaTrader 5")
    quit()

# Pengaturan simbol & timeframe
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M15
NUM_BARS = 264070  # Ambil 264070 data OHLCV (sekitar 6 bulan data dengan timeframe 15 menit)

# Ambil data dari MetaTrader 5
rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, NUM_BARS)

# Tutup koneksi MetaTrader 5
mt5.shutdown()

# Konversi data menjadi DataFrame
if rates is not None and len(rates) > 0:
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Konversi waktu ke datetime
    df.to_csv('XAUUSD_OHLCV.csv', index=False)
    print(f"Data berhasil disimpan ke file 'XAUUSD_OHLCV.csv'. Total data: {len(df)}")
else:
    print("Gagal mengambil data dari MetaTrader 5.")
