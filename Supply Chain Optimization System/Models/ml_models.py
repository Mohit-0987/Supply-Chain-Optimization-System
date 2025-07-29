import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import mlflow
import mlflow.sklearn
from datetime import datetime, timedelta
from scipy.stats import norm


class DemandForecastingModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, df):
        """Create features for demand forecasting"""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['quarter'] = df['timestamp'].dt.quarter

        # Lag features
        df['demand_lag_1'] = df['demand_quantity'].shift(1)
        df['demand_lag_7'] = df['demand_quantity'].shift(7)
        df['demand_lag_30'] = df['demand_quantity'].shift(30)

        # Rolling statistics
        df['demand_rolling_mean_7'] = df['demand_quantity'].rolling(window=7).mean()
        df['demand_rolling_std_7'] = df['demand_quantity'].rolling(window=7).std()

        # Promotion impact
        df['promotion_impact'] = df['promotion_active'].astype(int) * df['price']

        # Drop rows with NaN values
        df = df.dropna()

        return df

    def train(self, df):
        """Train the demand forecasting model"""
        with mlflow.start_run():
            df = self.prepare_features(df)

            feature_columns = [
                'hour', 'day_of_week', 'month', 'quarter',
                'demand_lag_1', 'demand_lag_7', 'demand_lag_30',
                'demand_rolling_mean_7', 'demand_rolling_std_7',
                'price', 'promotion_impact'
            ]

            X = df[feature_columns]
            y = df['demand_quantity']

            X_scaled = self.scaler.fit_transform(X)

            self.model.fit(X_scaled, y)