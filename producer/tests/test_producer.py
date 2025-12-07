"""
Unit tests for Upbit producer.

Tests the delivery callback, message formatting, and configuration.
"""

import json
import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add parent directory to path to import producer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from producer import delivery_report, BROKER, TOPIC


class TestDeliveryReport:
    """Test the Kafka delivery callback function."""
    
    def test_delivery_success(self, capsys):
        """Test successful message delivery prints correct output."""
        # Create a mock message object
        mock_msg = Mock()
        mock_msg.topic.return_value = "test-topic"
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 42
        
        # Call delivery_report with no error
        delivery_report(None, mock_msg)
        
        # Capture printed output
        captured = capsys.readouterr()
        
        # Assert success message was printed
        assert "✅ Delivered" in captured.out
        assert "test-topic" in captured.out
        assert "[0]" in captured.out
        assert "42" in captured.out
    
    def test_delivery_failure(self, capsys):
        """Test failed message delivery prints error."""
        # Create a mock message object (won't be used in error case)
        mock_msg = Mock()
        
        # Create a mock error
        mock_error = Exception("Connection refused")
        
        # Call delivery_report with error
        delivery_report(mock_error, mock_msg)
        
        # Capture printed output
        captured = capsys.readouterr()
        
        # Assert error message was printed
        assert "❌ Delivery failed" in captured.out
        assert "Connection refused" in captured.out


class TestConfiguration:
    """Test configuration constants."""
    
    def test_broker_config(self):
        """Test that BROKER is configured correctly."""
        assert BROKER == "localhost:19092"
        assert isinstance(BROKER, str)
        assert ":" in BROKER  # Should have host:port format
    
    def test_topic_config(self):
        """Test that TOPIC is configured correctly."""
        assert TOPIC == "upbit-ticks"
        assert isinstance(TOPIC, str)
        assert len(TOPIC) > 0  # Topic name should not be empty


class TestMessageFormatting:
    """Test message key/value formatting."""
    
    def test_message_key_encoding(self):
        """Test that message keys are properly encoded."""
        code = "KRW-BTC"
        encoded_key = code.encode()
        
        assert isinstance(encoded_key, bytes)
        assert encoded_key == b"KRW-BTC"
    
    def test_message_value_encoding(self):
        """Test that message values are properly JSON encoded."""
        sample_data = {
            "code": "KRW-BTC",
            "trade_price": 136000000,
            "timestamp": 1234567890
        }
        
        # Encode as it would be in producer
        encoded_value = json.dumps(sample_data).encode()
        
        # Verify it can be decoded back
        decoded = json.loads(encoded_value.decode())
        
        assert decoded["code"] == "KRW-BTC"
        assert decoded["trade_price"] == 136000000
        assert isinstance(encoded_value, bytes)


class TestSubscriptionMessage:
    """Test WebSocket subscription message format."""
    
    def test_subscription_message_structure(self):
        """Test that subscription message has correct structure."""
        subscribe_msg = [
            {"ticket": "tick-stream"},
            {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH", "KRW-XRP"]},
        ]
        
        # Check structure
        assert len(subscribe_msg) == 2
        assert "ticket" in subscribe_msg[0]
        assert "type" in subscribe_msg[1]
        assert "codes" in subscribe_msg[1]
        
        # Check values
        assert subscribe_msg[1]["type"] == "ticker"
        assert "KRW-BTC" in subscribe_msg[1]["codes"]
        
        # Verify it's JSON serializable
        json_str = json.dumps(subscribe_msg)
        assert isinstance(json_str, str)


# Pytest fixtures (optional but useful)
@pytest.fixture
def sample_ticker_data():
    """Sample ticker data from Upbit API."""
    return {
        "type": "ticker",
        "code": "KRW-BTC",
        "trade_price": 136000000.0,
        "trade_volume": 0.00123456,
        "timestamp": 1701878400000,
        "trade_timestamp": 1701878399123
    }


def test_ticker_data_parsing(sample_ticker_data):
    """Test that sample ticker data can be parsed correctly."""
    assert sample_ticker_data["code"] == "KRW-BTC"
    assert isinstance(sample_ticker_data["trade_price"], float)
    assert sample_ticker_data["trade_price"] > 0