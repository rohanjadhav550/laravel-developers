import mysql.connector
import os
from dotenv import load_dotenv
import requests
from functools import lru_cache
import time

load_dotenv()

# In-memory cache for API keys (expires after 5 minutes)
_api_key_cache = {}
_cache_ttl = 300  # 5 minutes

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql"),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_DATABASE", "laravel_app")
    )

def get_api_key_from_laravel(user_id):
    """
    Call Laravel API to get decrypted API key for a user.
    Includes caching, retry logic, and better error handling.
    """
    # Check cache first
    cache_key = f"user_{user_id}"
    if cache_key in _api_key_cache:
        cached_data, timestamp = _api_key_cache[cache_key]
        if time.time() - timestamp < _cache_ttl:
            print(f"Using cached API key for user {user_id}")
            return cached_data

    try:
        laravel_url = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")

        # Retry logic: try 3 times with increasing timeout
        max_retries = 3
        timeouts = [5, 10, 15]

        for attempt in range(max_retries):
            try:
                print(f"Calling Laravel API (attempt {attempt + 1}/{max_retries})...")
                response = requests.get(
                    f"{laravel_url}/api/internal/ai-settings",
                    json={"user_id": user_id},
                    timeout=timeouts[attempt]
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        # Cache the result
                        _api_key_cache[cache_key] = (data['data'], time.time())
                        print(f"Successfully fetched and cached API key for user {user_id}")
                        return data['data']
                else:
                    print(f"Laravel API returned status {response.status_code}: {response.text}")

                # If we get a response but it's not successful, don't retry
                break

            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)  # Wait 1 second before retry

            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)

        return None

    except Exception as e:
        print(f"Error calling Laravel API: {e}")
        return None

def get_llm_config(user_id=2):
    """
    Get LLM configuration for a specific user from Laravel API.
    All API keys must be configured in the main Laravel application.
    """
    # Get decrypted keys from Laravel API (with caching)
    settings = get_api_key_from_laravel(user_id)
    if settings:
        provider = settings['provider']
        api_key = settings['api_key']

        if provider == 'openai':
            return {'provider': 'OpenAI', 'api_key': api_key}
        elif provider == 'anthropic':
            return {'provider': 'Anthropic', 'api_key': api_key}

    print(f"WARNING: No AI configuration found for user {user_id}. Please configure AI settings at http://localhost:8000/settings/ai")
    return None
