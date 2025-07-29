# dags/supply_chain_pipeline.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Create DAG
dag = DAG(
    'supply_chain_optimization',
    default_args=default_args,
    description='Supply Chain Optimization Pipeline',
    schedule_interval=timedelta(hours=1),  # Run every hour
    catchup=False
)


def extract_data():
    """Extract data from various sources"""
    print("Extracting data from ERP system...")
    import requests
    import json

    # Mock ERP data
    erp_data = {
        'orders': [
            {'id': 1, 'product_id': 'P1001', 'quantity': 100, 'timestamp': str(datetime.now())},
            {'id': 2, 'product_id': 'P1002', 'quantity': 200, 'timestamp': str(datetime.now())}
        ]
    }

    # Save to temporary file
    with open('/tmp/erp_data.json', 'w') as f:
        json.dump(erp_data, f)

    print("Data extraction completed!")


def transform_data():
    """Transform and clean data"""
    print("Transforming data...")
    import pandas as pd
    import json

    # Read extracted data
    with open('/tmp/erp_data.json', 'r') as f:
        data = json.load(f)

    # Transform data
    df = pd.DataFrame(data['orders'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['processed_at'] = datetime.now()

    # Save transformed data
    df.to_csv('/tmp/transformed_data.csv', index=False)
    print("Data transformation completed!")


def load_data():
    """Load data into PostgreSQL"""
    print("Loading data into database...")
    import pandas as pd
    import psycopg2

    # Connect to database using the Docker service name
    conn = psycopg2.connect(
        host='postgres',
        database='supply_chain',
        user='admin',
        password='password'
    )

    # Read transformed data
    df = pd.read_csv('/tmp/transformed_data.csv')

    # Insert data
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO orders (product_id, quantity, timestamp, processed_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (row['product_id'], row['quantity'], row['timestamp'], row['processed_at']))

    conn.commit()
    conn.close()
    print("Data loading completed!")


# Define tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag
)

# Define task dependencies
extract_task >> transform_task >> load_task