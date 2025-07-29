# kafka_producer.py
from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime


class SupplyChainDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def generate_inventory_data(self):
        """Generate synthetic inventory data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'product_id': f'P{random.randint(1000, 9999)}',
            'location': random.choice(['WH001', 'WH002', 'WH003']),
            'quantity': random.randint(0, 1000),
            'reorder_point': random.randint(50, 200),
            'unit_cost': round(random.uniform(10, 100), 2)
        }

    def generate_demand_data(self):
        """Generate synthetic demand data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'product_id': f'P{random.randint(1000, 9999)}',
            'region': random.choice(['North', 'South', 'East', 'West']),
            'demand_quantity': random.randint(1, 50),
            'price': round(random.uniform(15, 150), 2),
            'promotion_active': random.choice([True, False])
        }

    def start_streaming(self):
        """Start streaming data to Kafka"""
        while True:
            # Send inventory data
            inventory_data = self.generate_inventory_data()
            self.producer.send('inventory-updates', inventory_data)

            # Send demand data
            demand_data = self.generate_demand_data()
            self.producer.send('demand-data', demand_data)

            print("Sent data...")
            time.sleep(5)  # Send every 5 seconds


# Run producer
if __name__ == "__main__":
    producer = SupplyChainDataProducer()
    producer.start_streaming()