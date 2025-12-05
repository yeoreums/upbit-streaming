from confluent_kafka import Consumer

c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'upbit-consumer-group',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['upbit-ticks'])

try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
        else:
            print(f"📨 {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    pass
finally:
    c.close()