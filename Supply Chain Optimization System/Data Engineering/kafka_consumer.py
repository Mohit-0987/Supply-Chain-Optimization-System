# kafka_consumer.py
from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime


class SupplyChainDataConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'inventory-updates',
            'demand-data',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',  # Start reading at the beginning of the topic
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        self.db_conn = psycopg2.connect(
            host='localhost',
            database='supply_chain',
            user='admin',
            password='password'
        )
        self.cursor = self.db_conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create database tables if they do not exist"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS inventory_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                product_id VARCHAR(50),
                location VARCHAR(50),
                quantity INTEGER,
                reorder_point INTEGER,
                unit_cost DECIMAL(10,2)
            )''',
            '''CREATE TABLE IF NOT EXISTS demand_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                product_id VARCHAR(50),
                region VARCHAR(50),
                demand_quantity INTEGER,
                price DECIMAL(10,2),
                promotion_active BOOLEAN
            )'''
        ]

        for table in tables:
            self.cursor.execute(table)
        self.db_conn.commit()

    def process_messages(self):
        """Process Kafka messages and store them in PostgreSQL"""
        print("Consumer started, waiting for messages...")
        for message in self.consumer:
            topic = message.topic
            data = message.value
            print(f"Received message from topic '{topic}': {data}")

            if topic == 'inventory-updates':
                self.store_inventory_data(data)
            elif topic == 'demand-data':
                self.store_demand_data(data)

    def store_inventory_data(self, data):
        """Store inventory data in the PostgreSQL database"""
        query = '''INSERT INTO inventory_data 
                   (timestamp, product_id, location, quantity, reorder_point, unit_cost)
                   VALUES (%s, %s, %s, %s, %s, %s)'''

        self.cursor.execute(query, (
            data['timestamp'],
            data['product_id'],
            data['location'],
            data['quantity'],
            data['reorder_point'],
            data['unit_cost']
        ))
        self.db_conn.commit()

    def store_demand_data(self, data):
        """Store demand data in the PostgreSQL database"""
        query = '''INSERT INTO demand_data 
                   (timestamp, product_id, region, demand_quantity, price, promotion_active)
                   VALUES (%s, %s, %s, %s, %s, %s)'''

        self.cursor.execute(query, (
            data['timestamp'],
            data['product_id'],
            data['region'],
            data['demand_quantity'],
            data['price'],
            data['promotion_active']
        ))
        self.db_conn.commit()


# Run the consumer
if __name__ == "__main__":
    consumer = SupplyChainDataConsumer()
    consumer.process_messages()