import requests
import json

def test_chat():
    url = "http://localhost:8001/ask"
    
    # 1. Initial greeting
    payload = {"question": "I want to build a Laravel e-commerce site."}
    print(f"Sending: {payload['question']}")
    try:
        response = requests.post(url, json=payload)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()
