from kafka import KafkaProducer
import json
from dotenv import load_dotenv
import os


class KafkaConnector:
    def __init__(self, topic='worker-0'):
        # load_dotenv()
        kafka_bootstrap_servers = 'localhost:29092'
        self.topic = 'workplace_1'
        self.producer = \
            KafkaProducer(bootstrap_servers=[kafka_bootstrap_servers],
                          value_serializer=lambda m: json.dumps(m).encode('ascii'),
                          retries=3)

    def send(self, json):
        # Asynchronous by default
        # produce keyed messages to enable hashed partitioning
        future = self.producer.send(self.topic, json)

        # Block for 'synchronous' sends
        record_metadata = future.get(timeout=10)

        # Successful result returns assigned partition and offset
        print(record_metadata.topic)
        print(record_metadata.partition)
        print(record_metadata.offset)


if __name__ == '__main__':
    conn = KafkaConnector()
    conn.send({'test': 'true'})
