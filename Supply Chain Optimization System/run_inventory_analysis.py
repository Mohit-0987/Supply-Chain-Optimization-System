import pandas as pd
import psycopg2
from Models.ml_models import InventoryOptimizer


def run_analysis():
    print("Starting inventory optimization analysis...")
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host='localhost',
            database='supply_chain',
            user='admin',
            password='password'
        )
        cursor = conn.cursor()
        print("Database connection successful.")

        # Load inventory and demand data
        inventory_df = pd.read_sql_query("SELECT * FROM inventory_data", conn)
        demand_df = pd.read_sql_query("SELECT * FROM demand_data", conn)
        print(f"Loaded {len(inventory_df)} inventory records and {len(demand_df)} demand records.")

        if demand_df.empty or inventory_df.empty:
            print("Not enough data to run analysis.")
            return

        # Combine data to get unit_cost for each product in demand_df
        # This assumes the latest unit_cost from inventory data is acceptable
        latest_costs = inventory_df.sort_values('timestamp').drop_duplicates('product_id', keep='last')[
            ['product_id', 'unit_cost']]
        analysis_df = pd.merge(demand_df, latest_costs, on='product_id', how='left').dropna()

        # Run optimization
        optimizer = InventoryOptimizer()
        optimization_results = optimizer.optimize_inventory_levels(analysis_df)
        print("Optimization calculation complete.")

        # Save results to a new table
        optimization_results.to_sql('inventory_optimization', conn, if_exists='replace', index=False)
        print("Successfully saved optimization results to the 'inventory_optimization' table.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()


if __name__ == "__main__":
    run_analysis()