from kafka import KafkaConsumer
from pymongo import MongoClient
import json
from dotenv import load_dotenv
import os

load_dotenv()

kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
mongodb_connection_string = os.getenv('MONGODB_CONNECTION_STRING')

# Set up Kafka consumer
consumer = KafkaConsumer(
    'your_topic_name',
    bootstrap_servers=[kafka_bootstrap_servers],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')))

# Set up MongoDB client
client = MongoClient(mongodb_connection_string)
db = client.your_database_name
collection = db.your_collection_name


def consume_messages():
    for message in consumer:
        data = message.value
        yield data


def process_messages():
    for data in consume_messages():
        collection.insert_one(data)

"""
var threeDaysAgo = new Date();
threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

# get all worker's duration within the most recent 3 days
db.collection_name.aggregate([
    { $unwind: "$report" },
    { $match: { "report.starttime": { $gte: threeDaysAgo.getTime() / 1000 } } },
    { $project: { "duration": "$report.duration" } }
])

# the average time taken for each action_id
db.collection_name.aggregate([
    { $unwind: "$report" },
    { $match: { "report.starttime": { $gte: threeDaysAgo.getTime() / 1000 } } },
    { $group: { _id: "$id", totalDuration: { $sum: "$report.duration" } } }
])

# the total duration in each report
db.collection_name.aggregate([
    { $unwind: "$report" },
    { $match: { "report.starttime": { $gte: threeDaysAgo.getTime() / 1000 } } },
    { $group: { _id: "$report.action_id", avgDuration: { $avg: "$report.duration" } } }
])

# the number of mistakes made in each day
db.collection_name.aggregate([
    { $unwind: "$report" },
    { $match: { "report.is_mistake": true } },
    {
        $group: {
            _id: {
                $dateToString: {
                    format: "%Y-%m-%d",
                    date: { $toDate: { $multiply: ["$report.starttime", 1000] } }
                }
            },
            count: { $sum: 1 }
        }
    }
])
"""

