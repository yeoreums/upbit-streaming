import asyncio
import json
import websockets
from confluent_kafka import Producer

BROKER = "localhost:19092"
TOPIC = "upbit-ticks"

def delivery_report(err, msg):
    # Kafka acknowledgment callback
    # This runs whenever a produced message is successfully delivered
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

async def produce_upbit():
    # Create Kafka producer instance (non-blocking, async-friendly)
    p = Producer({'bootstrap.servers': BROKER})

    uri = "wss://api.upbit.com/websocket/v1"
    
    # Subscription message for Upbit WebSocket
    # Requesting tick data for multiple KRW markets
    subscribe_msg = [
        {"ticket": "test"},
        {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH", "KRW-XRP"]}
    ]

    try:
        # Connect to Upbit websocket server
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps(subscribe_msg))
            print("🔗 Connected to Upbit WebSocket…")

            # Infinite loop: receive ticks → publish to Kafka
            while True:
                data = await ws.recv()  # Receive raw JSON string
                parsed = json.loads(data)

                # Print useful console info
                print(f"📈 {parsed['code']}: {parsed['trade_price']:,.0f} KRW")

                # Send message to Kafka
                # key = coin code
                # value = raw JSON tick data
                p.produce(
                    TOPIC,
                    key=parsed["code"].encode(),
                    value=json.dumps(parsed).encode(),
                    callback=delivery_report
                )

                # Let producer process delivery callbacks
                # poll(0) means "do not block"
                p.poll(0)

    except KeyboardInterrupt:
        # Nice shutdown when pressing Ctrl+C
        print("\n⏹️  Shutting down...")

    except Exception as e:
        # Catch all runtime errors (WebSocket, JSON, Kafka, etc.)
        print(f"❌ Error: {e}")

    finally:
        # Ensure all buffered messages are sent before exiting
        p.flush()

if __name__ == "__main__":
    # Run async main function
    asyncio.run(produce_upbit())
