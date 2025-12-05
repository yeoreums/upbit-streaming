# Upbit Streaming with Redpanda

A lightweight real-time streaming pipeline that captures crypto price ticks from Upbit and streams them into Redpanda.

- **Upbit WebSocket API**
- **Python async producer & consumer**
- **Redpanda** (Kafka-compatible streaming platform)
- **Docker** for local Redpanda setup

---

## 📂 Project Structure

```text
upbit-streaming/
├── upbit-redpanda/
│   └── docker-compose.yml
├── upbit-producer/
│   ├── producer.py
│   ├── consumer.py
│   └── requirements.txt
├── assets/
│   ├── console_screenshot.png
│   └── producer_output.png
└── README.md
```

---

## 🚀 How to Run
### 1. Start Redpanda (Docker)
Navigate to the docker directory and spin up the container.


```Bash
cd upbit-redpanda
docker-compose up -d
```
Dashboard: Access the Redpanda Console UI at http://localhost:8080.

### 2. Install Dependencies
Set up the Python environment and install the required packages.

```Bash
cd ../upbit-producer
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Producer
Start streaming data from the Upbit WebSocket.

```Bash
python producer.py
Streams real-time ticks for: KRW-BTC, KRW-ETH, KRW-XRP
```

### 4. Run the Consumer
Open a new terminal to consume the messages from Redpanda.

```Bash
source venv/bin/activate
python consumer.py
```
---

## 🏗 Architecture
```
graph LR
  A[Upbit WebSocket] --> B[Python Producer]
  B --> C[Redpanda]
  C --> D[Console UI]
  C --> E[Python Consumer]
```
---

### 📸 Screenshots
![Redpanda Console](assets/console_screenshot.png)
![Producer Output](assets/producer_output.jpg)
![jq Output](assets/jq_output.png)
