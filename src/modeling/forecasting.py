import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger

logger = setup_logger('forecasting', 'logs/forecasting.log')

# Try importing PyTorch
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not found. LSTM model will be skipped.")

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:i+seq_length]
        y = data[i+seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=50, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        lstm_out, _ = self.lstm(input_seq)
        # Select the output of the last time step
        last_time_step = lstm_out[:, -1, :]
        predictions = self.linear(last_time_step)
        return predictions

from datetime import timedelta

def forecast_metric(df, target_col, title, output_filename):
    logger.info(f"Forecasting {title}...")
    df = df.sort_values('date')
    data = df[target_col].values.reshape(-1, 1)
    
    # Normalize
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Parameters
    SEQ_LENGTH = 7 
    SPLIT_RATIO = 0.8
    
    # Calculate days needed to reach today + 90 days future
    last_date = df['date'].max()
    current_date = pd.Timestamp(datetime.now().date())
    
    days_to_present = (current_date - last_date).days
    if days_to_present < 0: days_to_present = 0
    
    FUTURE_DAYS = days_to_present + 90
    logger.info(f"Forecasting {days_to_present} days to reach present + 90 future days. Total: {FUTURE_DAYS} days.")
    
    if len(data) <= SEQ_LENGTH + 2:
        logger.warning(f"Not enough data points for {title} forecasting. Skipping.")
        return

    X, y = create_sequences(data_scaled, SEQ_LENGTH)
    
    split = int(len(X) * SPLIT_RATIO)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # --- Model Training (same as before) ---
    model = None
    y_pred_lstm = None
    rmse_lstm = 0
    
    # LSTM Training
    if TORCH_AVAILABLE and len(X_train) > 0:
        logger.info("Training LSTM Model (PyTorch)...")
        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.float32)
        X_test_t = torch.tensor(X_test, dtype=torch.float32)
        
        model = LSTMModel()
        loss_function = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        epochs = 100
        model.train()
        for i in range(epochs):
            optimizer.zero_grad()
            y_pred = model(X_train_t)
            loss = loss_function(y_pred, y_train_t)
            loss.backward()
            optimizer.step()
            
        model.eval()
        with torch.no_grad():
            y_pred_lstm_scaled = model(X_test_t).numpy()
        
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
        y_pred_lstm = scaler.inverse_transform(y_pred_lstm_scaled)
        
        mae_lstm = mean_absolute_error(y_test_actual, y_pred_lstm)
        rmse_lstm = np.sqrt(mean_squared_error(y_test_actual, y_pred_lstm))
        logger.info(f"LSTM MAE: {mae_lstm:.2f}, RMSE: {rmse_lstm:.2f}")

    # --- Future Forecasting ---
    future_dates = []
    future_preds = []
    
    if model:
        logger.info(f"Generating future forecast for {FUTURE_DAYS} days...")
        last_sequence = data_scaled[-SEQ_LENGTH:] # Start with the very last known sequence
        curr_seq = torch.tensor(last_sequence.reshape(1, SEQ_LENGTH, 1), dtype=torch.float32)
        
        last_date = df['date'].max()
        
        model.eval()
        for i in range(FUTURE_DAYS):
            with torch.no_grad():
                next_val_scaled = model(curr_seq)
            
            # Store prediction
            future_preds.append(next_val_scaled.item())
            
            # Update sequence: remove first, append new prediction
            next_val_seq = next_val_scaled.reshape(1, 1, 1)
            curr_seq = torch.cat((curr_seq[:, 1:, :], next_val_seq), dim=1)
            
            last_date += timedelta(days=1)
            future_dates.append(last_date)
            
        future_preds = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1))

    # --- Plotting ---
    plt.figure(figsize=(12, 6))
    
    # Plot Historical Data
    plt.plot(df['date'], df[target_col], label='Historical Data', color='black', alpha=0.5)
    
    # Plot Validation Predictions (on test set dates)
    if y_pred_lstm is not None and len(df['date']) > SEQ_LENGTH+split:
        test_dates = df['date'].iloc[SEQ_LENGTH+split:]
        plt.plot(test_dates, y_pred_lstm, label=f'Model Validation (RMSE={rmse_lstm:.0f})', color='green', alpha=0.8)

    # Plot Future Forecast
    if len(future_dates) > 0:
        plt.plot(future_dates, future_preds, label=f'Future Forecast (+{FUTURE_DAYS} days)', color='red', linestyle='dashed')

    plt.title(f'{title} Forecast')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    
    output_dir = 'docs/images'
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, output_filename)
    plt.savefig(plot_path)
    logger.info(f"Forecast plot saved to {plot_path}")
    plt.close()

def run_forecasting():
    # 1. Shelter Population
    shelter_path = 'data/gold/daily_shelter_stats.parquet'
    if os.path.exists(shelter_path):
        df = pd.read_parquet(shelter_path)
        forecast_metric(df, 'total_population', 'Shelter Population', 'forecast_results.png')
    
    # 2. Vendor Spend
    spend_path = 'data/gold/daily_vendor_spend.parquet'
    if os.path.exists(spend_path):
        df = pd.read_parquet(spend_path)
        forecast_metric(df, 'total_spend', 'Vendor Spend', 'forecast_spend.png')

if __name__ == "__main__":
    run_forecasting()
