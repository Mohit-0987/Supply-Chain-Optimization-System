# Use the official Airflow image as a base
FROM apache/airflow:2.5.0

# Install the python packages your DAG needs
RUN pip install --no-cache-dir \
    psycopg2-binary \
    pandas \
    requests \
    scikit-learn \
    joblib