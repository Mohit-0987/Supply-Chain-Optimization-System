# Supply Chain Optimization System


![Streamlit Dashboard Screenshot](https://github.com/Mohit-0987/Supply-Chain-Optimization-System/blob/main/Output%20Images/Streamlit_dashboard.png)

This repository hosts a robust Supply Chain Optimization System designed to enhance efficiency and decision-making in supply chain management. It leverages a modern data stack to handle real-time data, perform advanced analytics, and integrate machine learning models for forecasting and optimization.

## Features

* **Real-time Data Ingestion**: Utilizes Apache Kafka for streaming inventory updates and demand data.
* **Persistent Storage**: Stores all supply chain data in a PostgreSQL database with TimescaleDB for time-series capabilities.
* **Machine Learning Models**:
    * [cite_start]**Demand Forecasting**: Predicts future demand using a `RandomForestRegressor` model, tracking experiments with MLflow.
    * [cite_start]**Inventory Optimization**: Calculates optimal inventory levels, reorder points, and safety stock using an `InventoryOptimizer`[cite: 2, 4].
* [cite_start]**MLflow Integration**: Tracks machine learning experiments, models, and parameters, with MinIO as an S3-compatible artifact store.
* **Workflow Orchestration**: Manages and schedules data extraction, transformation, and loading (ETL) processes using Apache Airflow.
* **Interactive Dashboard**: Provides real-time insights and visualization of inventory, demand, and optimization results using Streamlit.
* [cite_start]**RESTful API**: Exposes an endpoint for demand prediction using FastAPI[cite: 1].
* **Containerized Environment**: All services are containerized using Docker and orchestrated with Docker Compose for easy setup and scalability.

## Architecture

The system's architecture is composed of several interconnected services:

* **`postgres`**: PostgreSQL database with TimescaleDB for storing raw and processed supply chain data.
* **`zookeeper` & `kafka`**: Core components for real-time data streaming.
* **`minio`**: An S3-compatible object storage server used by MLflow for artifact storage.
* **`mlflow`**: MLflow Tracking Server for managing machine learning experiments and models.
* **`airflow-webserver` & `airflow-scheduler`**: Apache Airflow instances for scheduling and monitoring data pipelines.
* **`grafana`**: A dashboarding tool for data visualization.
* **`kafka_producer.py`**: Generates and streams synthetic inventory and demand data to Kafka topics.
* **`kafka_consumer.py`**: Consumes data from Kafka and stores it in PostgreSQL.
* **`train_model.py`**: Script to train the demand forecasting model and log metrics/models to MLflow.
* **`run_inventory_analysis.py`**: Script to perform inventory optimization and store results in the database[cite: 2].
* [cite_start]**`api_server.py`**: A FastAPI application for serving demand predictions[cite: 1].
* **`streamlit_dashboard.py`**: An interactive Streamlit dashboard for visualizing key supply chain metrics.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Docker
* Docker Compose
* Python 3.9+ (for running producer, consumer, and dashboard scripts directly on the host)
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/supply-chain-optimization.git](https://github.com/your-username/supply-chain-optimization.git)
    cd supply-chain-optimization
    ```

2.  **Build and Start Docker services:**
    This command will build the necessary Docker images and then start all the services defined in `docker-compose.yml` (PostgreSQL, Kafka, Zookeeper, MinIO, MLflow, Airflow, Grafana) in detached mode (`-d`).
    ```bash
    docker-compose build
    docker-compose up -d
    ```
    Allow some time for all services to initialize, especially Airflow's database and user setup.

3.  **Install Python dependencies on your host machine:**
    You'll need these to run the `kafka_producer.py`, `kafka_consumer.py`, `train_model.py`, `run_inventory_analysis.py`, and `streamlit_dashboard.py` scripts directly from your host.
    ```bash
    pip install kafka-python psycopg2-binary pandas scikit-learn joblib mlflow streamlit plotly
    ```

4.  **Run Kafka Producer:**
    Open a new terminal and execute the Kafka producer script. This will start sending synthetic inventory and demand data to the Kafka topics (`inventory-updates` and `demand-data`). You will see "Sent data..." messages in the terminal.
    ```bash
    python "Data Engineering/kafka_producer.py"
    ```

5.  **Run Kafka Consumer:**
    Open another new terminal and execute the Kafka consumer script. This script will receive the data from Kafka and store it into the PostgreSQL database. You will see "Received message from topic..." messages.
    ```bash
    python "Data Engineering/kafka_consumer.py"
    ```

6.  **Run Streamlit Dashboard:**
    Open a third terminal and run the Streamlit dashboard. This will provide a local URL (e.g., `http://localhost:8501`) where you can view the real-time supply chain analytics.
    ```bash
    streamlit run "Dash Board/streamlit_dashboard.py"
    ```

7.  **Train the Machine Learning Model:**
    Once the producer and consumer have been running for a few minutes and some data has accumulated in the PostgreSQL database, you can train the demand forecasting model. [cite_start]This script will connect to PostgreSQL, load data, train the `DemandForecastingModel`, and log the experiment run to MLflow.
    ```bash
    python train_model.py
    ```

8.  **Run Inventory Analysis:**
    After the training, you can run the inventory optimization analysis. [cite_start]This script will read inventory and demand data from PostgreSQL, perform optimization calculations, and save the results back to the database[cite: 2].
    ```bash
    python run_inventory_analysis.py
    ```
9. **After you are finished using the project, remember to close all open terminal windows and local host websites, then run docker-compose down in your project's root directory to stop and remove the Docker containers and networks.**
    ```bash
    docker-compose down
    ```
    **it will stop all the services**

### Accessing UIs and Dashboards

Once the services are running and scripts have been executed, you can access the various UIs:

* **Streamlit Dashboard**: The link provided in your terminal after running `streamlit run "Dash Board/streamlit_dashboard.py"` (typically `http://localhost:8501`). Here you can see metrics like "Total Products Tracked", "Total Current Inventory", and "Products at Risk of Stockout".
* **Airflow UI**: `http://localhost:8080` (Login with `admin`/`admin`). You can monitor the `supply_chain_optimization` DAG here.
* **MLflow UI**: `http://localhost:5000`. You can review the logged machine learning experiments and models.
* **MinIO Console**: `http://localhost:9001` (Login with `admin`/`password123`). This is where MLflow stores its artifacts.
* **Grafana**: `http://localhost:3000` (Login with `admin`/`admin`). (Note: This project sets up Grafana but doesn't include pre-configured dashboards for it. You would need to set those up manually to visualize data).
* [cite_start]**FastAPI API Docs**: If you choose to run `api_server.py` separately (it's not part of the `docker-compose up` flow by default in your setup), you can access its interactive API documentation at `http://localhost:8000/docs` (assuming you run it on port 8000)[cite: 1].

## Project Structure


    ├── Supply Chain Optimization System/  # Main Folder

         ├── Dags/
             └── supply_chain_pipeline.py  # Airflow DAG for ETL 
         
         
         ├── Dash Board/
             └── streamlit_dashboard.py    # Streamlit interactive dashboard 
         
         
         ├── Data Engineering/
             └── kafka_consumer.py         # Kafka consumer to ingest data into PostgreSQL 
         
             └── kafka_producer.py         # Kafka producer to generate synthetic data 
         
         
         ├── Models/
             └── ml_models.py              # Machine Learning models (DemandForecastingModel, InventoryOptimizer) 
         
         ├── api_server.py                 # FastAPI for demand prediction 
         
         ├── docker-compose.yml            # Defines and links all Docker services 
         
         
         ├── Dockerfile                    # Dockerfile for Airflow environment 
         
         
         ├── Dockerfile.mlflow             # Dockerfile for MLflow server dependencies 
         
         
         ├── init-db.sh                    # Script to initialize PostgreSQL databases 
         
         ├── run_inventory_analysis.py     # Script to run inventory optimization 
         
         ├── train_model.py                # Script to train demand forecasting model with MLflow

# If you encounter any issues or have questions, please feel free to reach out to me via my portfolio or Gmail
