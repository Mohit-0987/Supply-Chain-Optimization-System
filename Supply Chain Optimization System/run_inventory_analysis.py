import pandas as pd
import psycopg2
from Models.ml_models import InventoryOptimizer
# from sqlalchemy.types import String, Float # We no longer need these for dtype_mapping, but we need create_engine
from sqlalchemy import create_engine  # Import create_engine


def create_optimization_table(cursor, conn):
    """Create the inventory_optimization table if it does not exist, or drop and recreate if needed."""
    try:
        # Drop table if it exists to ensure a clean slate, similar to if_exists='replace'
        cursor.execute("DROP TABLE IF EXISTS inventory_optimization CASCADE;")
        conn.commit()
        print("Dropped existing 'inventory_optimization' table (if any).")

        # Create the table with explicit column types
        # Ensure column names and types match your optimization_results DataFrame
        cursor.execute('''
            CREATE TABLE inventory_optimization (
                product_id VARCHAR(50),
                annual_demand DECIMAL(18,2),
                avg_daily_demand DECIMAL(18,2),
                unit_cost DECIMAL(10,2),
                eoq DECIMAL(18,2),
                reorder_point DECIMAL(18,2),
                safety_stock DECIMAL(18,2)
            )
        ''')
        conn.commit()
        print("Created 'inventory_optimization' table.")
    except Exception as e:
        print(f"Error creating/recreating 'inventory_optimization' table: {e}")
        conn.rollback()


def run_analysis():
    print("Starting inventory optimization analysis...")

    # Initialize engine and conn to None
    engine = None
    conn = None

    try:
        # --- NEW: Create a SQLAlchemy engine for PostgreSQL ---
        # The database URI format is: 'postgresql+psycopg2://user:password@host:port/database'
        db_uri = 'postgresql+psycopg2://admin:password@localhost:5432/supply_chain'
        engine = create_engine(db_uri)
        print("SQLAlchemy engine created.")
        # --- END NEW ---

        # Connect using psycopg2 directly for cursor operations (like creating table)
        # We still need this for explicit cursor operations like create_optimization_table
        conn = psycopg2.connect(
            host='localhost',
            database='supply_chain',
            user='admin',
            password='password'
        )
        cursor = conn.cursor()
        print("Psycopg2 connection successful.")

        # Call the table creation function using the psycopg2 connection
        create_optimization_table(cursor, conn)

        # Load inventory and demand data using the SQLAlchemy engine
        # pandas.read_sql_query works better with an engine
        inventory_df = pd.read_sql_query("SELECT * FROM inventory_data", engine)  # Use engine here
        inventory_df['product_id'] = inventory_df['product_id'].astype(str)

        demand_df = pd.read_sql_query("SELECT * FROM demand_data", engine)  # Use engine here
        demand_df['product_id'] = demand_df['product_id'].astype(str)

        print(f"Loaded {len(inventory_df)} inventory records and {len(demand_df)} demand records.")

        if demand_df.empty or inventory_df.empty:
            print("Not enough data to run analysis.")
            return

        # Combine data to get unit_cost for each product in demand_df
        latest_costs = inventory_df.sort_values('timestamp').drop_duplicates('product_id', keep='last')[
            ['product_id', 'unit_cost']]
        latest_costs['product_id'] = latest_costs['product_id'].astype(str)

        analysis_df = pd.merge(demand_df, latest_costs, on='product_id', how='left').dropna()

        # Run optimization
        optimizer = InventoryOptimizer()
        optimization_results = optimizer.optimize_inventory_levels(analysis_df)
        print("Optimization calculation complete.")

        # Final check for product_id type before saving
        optimization_results['product_id'] = optimization_results['product_id'].astype(str)

        # Save results to the already created table using the SQLAlchemy engine
        optimization_results.to_sql(
            'inventory_optimization',
            engine,  # Use engine here
            if_exists='append',
            index=False,
        )
        print("Successfully saved optimization results to the 'inventory_optimization' table.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the SQLAlchemy engine connection pool
        if engine is not None:
            engine.dispose()
        # Close the psycopg2 connection if it was opened
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    run_analysis()