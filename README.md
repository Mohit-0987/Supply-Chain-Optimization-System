# Supply Chain Optimization System

This repository hosts a robust Supply Chain Optimization System designed to enhance efficiency and decision-making in supply chain management. It leverages a modern data stack to handle real-time data, perform advanced analytics, and integrate machine learning models for forecasting and optimization.

## Features

* **Real-time Data Ingestion**: Utilizes Apache Kafka for streaming inventory updates and demand data.
* [cite_start]**Persistent Storage**: Stores all supply chain data in a PostgreSQL database with TimescaleDB for time-series capabilities.
* **Machine Learning Models**:
    * **Demand Forecasting**: Predicts future demand using a `RandomForestRegressor` model, tracking experiments with MLflow.
    * **Inventory Optimization**: Calculates optimal inventory levels, reorder points, and safety stock using an `InventoryOptimizer`.
* [cite_start]**MLflow Integration**: Tracks machine learning experiments, models, and parameters, with MinIO as an S3-compatible artifact store.
* **Workflow Orchestration**: Manages and schedules data extraction, transformation, and loading (ETL) processes using Apache Airflow.
* **Interactive Dashboard**: Provides real-time insights and visualization of inventory, demand, and optimization results using Streamlit.
* **RESTful API**: Exposes an endpoint for demand prediction using FastAPI.
* [cite_start]**Containerized Environment**: All services are containerized using Docker and orchestrated with Docker Compose for easy setup and scalability[cite: 1, 4].

## Architecture

The system's architecture is composed of several interconnected services:

* [cite_start]**`postgres`**: PostgreSQL database with TimescaleDB for storing raw and processed supply chain data.
* [cite_start]**`zookeeper` & `kafka`**: Core components for real-time data streaming.
* [cite_start]**`minio`**: An S3-compatible object storage server used by MLflow for artifact storage.
* [cite_start]**`mlflow`**: MLflow Tracking Server for managing machine learning experiments and models.
* [cite_start]**`airflow-webserver` & `airflow-scheduler`**: Apache Airflow instances for scheduling and monitoring data pipelines.
* [cite_start]**`grafana`**: (Optional, for future integration) A dashboarding tool for data visualization.
* **`kafka_producer.py`**: Generates and streams synthetic inventory and demand data to Kafka topics.
* **`kafka_consumer.py`**: Consumes data from Kafka and stores it in PostgreSQL.
* **`train_model.py`**: Script to train the demand forecasting model and log metrics/models to MLflow.
* **`run_inventory_analysis.py`**: Script to perform inventory optimization and store results in the database.
* **`api_server.py`**: A FastAPI application for serving demand predictions.
* **`streamlit_dashboard.py`**: An interactive Streamlit dashboard for visualizing key supply chain metrics.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Docker
* Docker Compose

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/supply-chain-optimization.git](https://github.com/your-username/supply-chain-optimization.git)
    cd supply-chain-optimization
    ```

2.  **Build Docker images:**
    ```bash
    docker-compose build
    ```
    This will build images for Airflow  and MLflow.

3.  **Start the services:**
    ```bash
    docker-compose up -d
    ```
    This command will start all the services defined in `docker-compose.yml` in detached mode, including PostgreSQL, Kafka, Zookeeper, MinIO, MLflow, Airflow, and Grafana.

4.  **Initialize Airflow (first time only):**
    Wait for the `airflow-webserver` and `airflow-scheduler` containers to be healthy. You can check their status with `docker-compose ps`.
    Airflow will automatically set up the database and create an admin user on startup as defined in `docker-compose.yml`.

5.  **Run Kafka Producer (in a new terminal):**
    This will start streaming synthetic inventory and demand data into Kafka.
    ```bash
    docker-compose exec kafka /bin/bash -c "python /app/Data\ Engineering/kafka_producer.py" # Assuming kafka_producer.py is copied to /app/Data Engineering/ within the kafka container. Adjust path as necessary.
    # Alternatively, if you have a separate Python environment on your host:
    # python Data\ Engineering/kafka_producer.py
    ```
    *Note: The `kafka_producer.py` and `kafka_consumer.py` are intended to be run from your host machine or within a dedicated application container. For this `docker-compose.yml`, they are not explicitly made into separate services. You would run them from your host after the `docker-compose up` command, ensuring they can connect to `localhost:9092` and `localhost:5432` respectively.*

6.  **Run Kafka Consumer (in another new terminal):**
    This will consume data from Kafka and store it in PostgreSQL.
    ```bash
    docker-compose exec postgres /bin/bash -c "python /app/Data\ Engineering/kafka_consumer.py" # Assuming kafka_consumer.py is copied to /app/Data Engineering/ within the postgres container. Adjust path as necessary.
    # Alternatively, if you have a separate Python environment on your host:
    # python Data\ Engineering/kafka_consumer.py
    ```

7.  **Train the ML model:**
    Once some data has been ingested (allow the `kafka_producer.py` and `kafka_consumer.py` to run for a few minutes), you can train the demand forecasting model:
    ```bash
    docker-compose exec airflow-webserver /bin/bash -c "python /opt/airflow/dags/train_model.py" # Adjust path as necessary
    # Alternatively, if you have a separate Python environment on your host:
    # python train_model.py
    ```
    This script will connect to PostgreSQL, load data, train the `DemandForecastingModel`, and log the run to MLflow.

8.  **Run Inventory Analysis:**
    ```bash
    docker-compose exec airflow-webserver /bin/bash -c "python /opt/airflow/dags/run_inventory_analysis.py" # Adjust path as necessary
    # Alternatively, if you have a separate Python environment on your host:
    # python run_inventory_analysis.py
    ```
    This script will calculate and store inventory optimization results.

9.  **Access the Dashboards and UIs:**
    * [cite_start]**Airflow UI**: `http://localhost:8080` (Login with `admin`/`admin`) 
    * [cite_start]**MLflow UI**: `http://localhost:5000` 
    * **MinIO Console**: `http://localhost:9001` (Login with `admin`/`password123`) 
    * [cite_start]**Grafana**: `http://localhost:3000` (Login with `admin`/`admin`) 
    * **Streamlit Dashboard**:
        ```bash
        streamlit run Dash\ Board/streamlit_dashboard.py
        ```
        (Run this from your host machine where Streamlit is installed. You might need to `pip install streamlit plotly psycopg2-binary`).
    * **FastAPI**: `http://localhost:8000/docs` (if you run `api_server.py` separately)

## Project Structure
