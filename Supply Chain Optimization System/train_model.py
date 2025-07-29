import pandas as pd
import psycopg2
from Models.ml_models import DemandForecastingModel
import os

# --- ADD THESE LINES ---
# Tell the script where to find the MLflow server
os.environ['MLFLOW_TRACKING_URI'] = 'http://localhost:5000'

# Provide credentials for MinIO (S3 storage)
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'password123'
# --------------------


print("Connecting to database...")
try:
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        host='localhost',
        database='supply_chain',
        user='admin',
        password='password'
    )

    print("Loading data for training...")
    # Load the last 90 days of data for a stable training set
    demand_df = pd.read_sql_query("SELECT * FROM demand_data WHERE timestamp > NOW() - INTERVAL '90 days'", conn)
    conn.close()

    # Ensure there's enough data to create lag/rolling features
    if len(demand_df) > 30:
        print(f"Sufficient data found ({len(demand_df)} records). Training model...")

        # Initialize and train the model
        forecasting_model = DemandForecastingModel()
        forecasting_model.train(demand_df)

        print("\nModel training complete!")
        print("Check MLflow UI at http://localhost:5000 to see your experiment run.")
    else:
        print(f"Not enough data to train the model yet. Found {len(demand_df)} records, but need more than 30.")

except Exception as e:
    print(f"An error occurred: {e}")