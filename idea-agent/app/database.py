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
                    params={"user_id": user_id},
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

def get_llm_config(user_id=2, ai_provider=None, ai_api_key=None):
    """
    Get LLM configuration for a specific user.
    If ai_provider and ai_api_key are provided, use them directly.
    Otherwise, fetch from Laravel API.
    """
    # If AI settings are passed directly, use them (avoids circular API calls)
    if ai_provider and ai_api_key:
        if ai_provider.lower() == 'openai':
            return {'provider': 'OpenAI', 'api_key': ai_api_key}
        elif ai_provider.lower() == 'anthropic':
            return {'provider': 'Anthropic', 'api_key': ai_api_key}

    # Otherwise, get decrypted keys from Laravel API (with caching)
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

def save_conversation_metadata(user_id, thread_id, title=None, message_count=None, project_id=None):
    """
    Save or update conversation metadata in Laravel's MySQL database.
    The actual conversation messages are stored in Redis via LangGraph's RedisSaver.
    """
    try:
        laravel_url = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")

        payload = {
            'user_id': user_id,
            'thread_id': thread_id,
        }

        if title:
            payload['title'] = title
        if message_count is not None:
            payload['message_count'] = message_count
        if project_id:
            payload['project_id'] = project_id

        response = requests.post(
            f"{laravel_url}/api/internal/conversations",
            json=payload,
            timeout=5
        )

        if response.status_code == 200:
            print(f"Conversation metadata saved: {thread_id}")
            return response.json().get('data')
        else:
            print(f"Failed to save conversation metadata: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error saving conversation metadata: {e}")
        return None

def save_requirements_to_laravel(thread_id, requirements):
    """
    Save requirements document to Laravel's MySQL database.
    """
    try:
        laravel_url = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")

        payload = {
            'thread_id': thread_id,
            'requirements': requirements,
        }

        response = requests.post(
            f"{laravel_url}/api/internal/conversations/requirements",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"Requirements saved for thread {thread_id}")
            return response.json().get('data')
        else:
            print(f"Failed to save requirements: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error saving requirements: {e}")
        return None

def save_solution_to_laravel(thread_id, solution):
    """
    Save solution document to Laravel's MySQL database.
    """
    try:
        laravel_url = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")

        payload = {
            'thread_id': thread_id,
            'solution': solution,
        }

        response = requests.post(
            f"{laravel_url}/api/internal/conversations/solution",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"Solution saved for thread {thread_id}")
            return response.json().get('data')
        else:
            print(f"Failed to save solution: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error saving solution: {e}")
        return None
