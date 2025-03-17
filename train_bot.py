import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import MetaTrader5 as mt5

# Koneksi ke MetaTrader 5
mt5.initialize()

# Ambil data XAUUSD dari MetaTrader 5
symbol = "XAUUSD"
num_bars = 100000  # Ambil 100.000 data OHLCV
data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, num_bars)
df = pd.DataFrame(data)[["open", "high", "low", "close", "tick_volume"]]

# Tutup koneksi MT5
mt5.shutdown()

# Normalisasi Data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

# Buat dataset untuk LSTM
def create_dataset(data, time_step=60):
    X, Y = [], []
    for i in range(len(data) - time_step - 1):
        X.append(data[i:(i + time_step), :])
        Y.append(data[i + time_step, 3])  # Prediksi harga penutupan (close)
    return np.array(X), np.array(Y)

# Persiapkan data untuk training
time_step = 60
X, Y = create_dataset(scaled_data, time_step)

# Pisahkan data menjadi training dan testing
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Bangun Model LSTM
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(time_step, X.shape[2])),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# Latih model
epochs = 100
batch_size = 64
model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=epochs, batch_size=batch_size, verbose=1)

# Simpan model terlatih
model.save("lstm_model.h5")
