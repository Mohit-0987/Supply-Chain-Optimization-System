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

            # Log parameters and metrics (example)
            mlflow.log_params({
                "n_estimators": self.model.n_estimators,
                "random_state": self.model.random_state
            })
            # Predictions for evaluation
            y_pred = self.model.predict(X_scaled)
            mae = mean_absolute_error(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            mlflow.log_metrics({"mae": mae, "rmse": rmse})

            # Log the model
            mlflow.sklearn.log_model(self.model, "random_forest_model")
            self.is_trained = True

            # Save scaler and feature columns for prediction
            joblib.dump(self.scaler, "scaler.pkl")
            joblib.dump(feature_columns, "feature_columns.pkl")
            mlflow.log_artifact("scaler.pkl")
            mlflow.log_artifact("feature_columns.pkl")


# NEW CLASS: InventoryOptimizer
class InventoryOptimizer:
    def optimize_inventory_levels(self, df):
        """
        Optimizes inventory levels, calculating EOQ, reorder point, and safety stock.
        Assumes df contains 'product_id', 'demand_quantity', 'unit_cost'.
        Additional parameters like holding_cost_rate, ordering_cost, lead_time_days
        would typically be fixed or pulled from a config/DB.
        """
        results = []

        # Example fixed parameters (you might want to make these configurable)
        holding_cost_rate = 0.20  # 20% of unit cost annually
        ordering_cost = 50.0  # Cost per order
        lead_time_days = 7  # Lead time in days
        service_level_z = norm.ppf(0.95)  # Z-score for 95% service level for 95% service level

        # Ensure 'product_id' is suitable for grouping
        df['product_id'] = df['product_id'].astype(str)

        for product_id, product_df in df.groupby('product_id'):
            if product_df['demand_quantity'].empty or product_df['unit_cost'].empty:
                continue

            # Calculate annual demand. Assuming historical demand in 'demand_quantity'
            # For simplicity, if timestamp distribution is dense, sum and annualize.
            # More robust would be to ensure 'annual_demand' is truly annual.
            # Here, we'll estimate annual demand based on available data length.
            # Let's assume demand_quantity is daily for estimation.
            # This is a simplification; ideally, you'd have a time series with clear daily/weekly/monthly sums.

            # Count unique days with demand to estimate period length
            unique_days = product_df['timestamp'].dt.date.nunique()
            if unique_days > 0:
                avg_daily_demand = product_df['demand_quantity'].sum() / unique_days
                annual_demand = avg_daily_demand * 365
            else:
                avg_daily_demand = 0
                annual_demand = 0

            # Use the latest unit cost for the product
            unit_cost = product_df['unit_cost'].iloc[-1] if not product_df['unit_cost'].empty else 0.0

            if annual_demand <= 0 or unit_cost <= 0 or holding_cost_rate <= 0:
                # Cannot calculate EOQ, set to 0 or handle as needed
                eoq = 0.0
                reorder_point = 0.0
                safety_stock = 0.0
            else:
                # Calculate EOQ (Economic Order Quantity)
                eoq = np.sqrt((2 * annual_demand * ordering_cost) / (unit_cost * holding_cost_rate))

                # Calculate demand standard deviation during lead time
                # Using standard deviation of daily demand, and multiplying by sqrt(lead_time_days)
                # A more robust approach might analyze historical demand during lead times.
                daily_demands = product_df.groupby(product_df['timestamp'].dt.date)[
                    'demand_quantity'].sum().reset_index()
                demand_std_dev = daily_demands['demand_quantity'].std() if daily_demands[
                                                                               'demand_quantity'].count() > 1 else 0

                lead_time_demand_std = demand_std_dev * np.sqrt(lead_time_days)

                # Calculate Safety Stock
                safety_stock = service_level_z * lead_time_demand_std

                # Calculate Reorder Point
                reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

            results.append({
                'product_id': product_id,
                'annual_demand': annual_demand,
                'avg_daily_demand': avg_daily_demand,
                'unit_cost': unit_cost,
                'eoq': eoq,
                'reorder_point': reorder_point,
                'safety_stock': safety_stock
            })

        return pd.DataFrame(results)