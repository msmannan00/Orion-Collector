import os
import subprocess
import sys
import time
import redis
import requests

from crawler.crawler_services.shared.env_handler import env_handler
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS


def check_tor_status():
    try:
        tor_proxy = "socks5h://127.0.0.1:9150"
        response = requests.get("http://check.torproject.org", proxies={"http": tor_proxy}, timeout=100)
        response.raise_for_status()
        if response.status_code != 200:
            print("Tor is running but not working as expected.")
            sys.exit(1)
    except Exception as ex:
        print(f"Error: Tor is not running or accessible. Details: {ex}")
        sys.exit(1)


def check_redis_status():
    try:
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        if not redis_client.ping():
            print("Redis server is running but not responding.")
            sys.exit(1)
    except Exception as ex:
        print(f"Error: Redis server is not running or accessible. Details: {ex}")
        sys.exit(1)


def check_orion_status_and_token():
    try:
        production = env_handler.get_instance().env("PRODUCTION") == "1"
        server_url = env_handler.get_instance().env("S_SERVER") if production else "http://localhost:8080"
        requests.get(server_url, timeout=5)
    except Exception as ex:
        print(f"Orion server is not running or accessible. Details: {ex}")
        sys.exit(1)

    try:
        username = env_handler.get_instance().env("S_SERVER_USERNAME")
        password = env_handler.get_instance().env("S_SERVER_PASSWORD")
        S_TOKEN = f"{server_url}/api/token"

        MAX_RETRIES = 3
        RETRY_DELAY = 3

        for _ in range(MAX_RETRIES):
            try:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                payload = {'username': username, 'password': password}

                response = requests.post(S_TOKEN, data=payload, headers=headers, timeout=10)
                if response.status_code != 200:
                    time.sleep(RETRY_DELAY)
                    continue

                data = response.json()
                token = data.get("access_token")
                if token:
                    redis_controller().invoke_trigger(REDIS_COMMANDS.S_SET_STRING, ["bearertoken", token, None])
                    return

            except Exception:
                time.sleep(RETRY_DELAY)

        print("Error: Failed to obtain Orion token after retries.")
        sys.exit(1)

    except Exception as ex:
        print(f"Token request setup failed. Details: {ex}")
        sys.exit(1)

def run_env_update_script():
    script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    script_path = os.path.join(script_dir, "run.sh")
    subprocess.run(["chmod", "+x", script_path], check=True)
    subprocess.run([script_path], check=True, cwd=script_dir)

def parse_data(model):
    try:
        production = env_handler.get_instance().env("PRODUCTION") == "1"
        server_url = env_handler.get_instance().env("S_SERVER") if production else "http://localhost:8080"
        url = f"{server_url}/api/nlp/parse/ai"

        token = redis_controller().invoke_trigger(REDIS_COMMANDS.S_GET_STRING, ["bearertoken", None, None])
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.post(url, json={"data": model}, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as ex:
        return {"error": f"Failed to connect to Orion NLP parse API: {str(ex)}"}

def check_services_status():
    check_tor_status()
    check_redis_status()
    check_orion_status_and_token()
