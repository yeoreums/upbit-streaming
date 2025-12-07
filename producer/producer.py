"""
Upbit WebSocket → Redpanda Streaming Producer.

Connects to Upbit's WebSocket API, receives real-time cryptocurrency
ticker data, and streams each tick to a Redpanda (Kafka-compatible) topic.

Usage:
    python producer.py

Requirements:
    - Redpanda running at localhost:19092
    - Packages: confluent-kafka, websockets
"""

import asyncio
import json
import websockets
from confluent_kafka import Producer

BROKER = "localhost:19092"
TOPIC = "upbit-ticks"


def delivery_report(err, msg):
    """
    Handle Kafka delivery results.
    
    Called by the Kafka Producer when a message is either successfully delivered
    or fails to deliver.
    
    Args:
        err: Error object if delivery failed, otherwise None.
        msg: Message object containing metadata (topic, partition, offset).
    """
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")


async def produce_upbit():
    """
    Stream Upbit ticker data to Redpanda.
    
    Opens a WebSocket connection to Upbit, subscribes to KRW markets
    (BTC, ETH, XRP), receives real-time ticks, and publishes each tick
    to the Redpanda topic defined in `TOPIC`.
    
    Runs indefinitely until interrupted. All pending messages are flushed
    before shutdown.
    
    Raises:
        websockets.exceptions.WebSocketException: If the WebSocket connection fails.
        confluent_kafka.KafkaException: If Kafka message production encounters an error.
    """
    p = Producer({'bootstrap.servers': BROKER})
    uri = "wss://api.upbit.com/websocket/v1"
    
    subscribe_msg = [
        {"ticket": "tick-stream"},
        {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH", "KRW-XRP"]},
    ]

    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps(subscribe_msg))
            print("🔗 Connected to Upbit WebSocket…")

            while True:
                data = await ws.recv()
                parsed = json.loads(data)

                print(f"📈 {parsed['code']}: {parsed['trade_price']:,.0f} KRW")

                p.produce(
                    TOPIC,
                    key=parsed["code"].encode(),
                    value=json.dumps(parsed).encode(),
                    callback=delivery_report,
                )
                p.poll(0)

    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        p.flush()


if __name__ == "__main__":
    asyncio.run(produce_upbit())