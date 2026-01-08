import os
import requests
from dotenv import load_dotenv

load_dotenv()

proxy_username = os.getenv("PROXY_USERNAME")
proxy_password = os.getenv("PROXY_PASSWORD")

proxies = {
    "http": f"http://{proxy_username}-rotate:{proxy_password}@p.webshare.io:80/",
    "https": f"http://{proxy_username}-rotate:{proxy_password}@p.webshare.io:80/",
}

print("Testing proxy connection...")
try:
    response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
