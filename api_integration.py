# api_integration.py
import requests
import json
from urllib.parse import urljoin
from config import SHODAN_API_KEY, VIRUSTOTAL_API_KEY, IP_API_BASE_URL, MY_API_BASE_URL


def _make_api_call(url, api_type, headers=None, timeout=10):
    """Helper function to make API calls with error handling."""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"{api_type} API error: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Error decoding JSON from {api_type}: {e}"}


def shodan_lookup(ip):
    """Retrieve information from Shodan."""
    if not ip:
        return {"error": "IP Address cannot be empty."}
    if not SHODAN_API_KEY:
        return {"message": "Shodan API Key not configured"}  # Return a message if the API key is missing
    url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}"
    return _make_api_call(url, "Shodan")


def virustotal_lookup(domain):
    """Retrieve information from VirusTotal."""
    if not domain:
        return {"error": "Domain cannot be empty."}
    if not VIRUSTOTAL_API_KEY:
        return {"error": "VirusTotal API key not configured"}
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    return _make_api_call(url, "VirusTotal", headers=headers)


def my_api_whois(domain):
    """Retrieve WHOIS information from the internal API."""
    if not domain:
        return {"error": "Domain cannot be empty."}
    url = urljoin(MY_API_BASE_URL, f"/whois/{domain}")
    return _make_api_call(url, "My API")


def my_api_geoip(ip):
    """Retrieve GeoIP information from the internal API."""
    if not ip:
        return {"error": "IP Address cannot be empty."}
    url = urljoin(MY_API_BASE_URL, f"/geoip/{ip}")
    return _make_api_call(url, "My API")


def my_api_ssl(domain):
    """Retrieve SSL information from the internal API."""
    if not domain:
        return {"error": "Domain cannot be empty."}
    url = urljoin(MY_API_BASE_URL, f"/ssl/{domain}")
    return _make_api_call(url, "My API")


def my_api_phone(query):
    """Retrieve phone number information from the internal API."""
    if not query:
        return {"error": "Query cannot be empty."}
    url = urljoin(MY_API_BASE_URL, f"/phone/{query}")
    return _make_api_call(url, "My API")


def my_api_email(query):
    """Retrieve email information from the internal API."""
    if not query:
        return {"error": "Query cannot be empty."}
    url = urljoin(MY_API_BASE_URL, f"/email/{query}")
    return _make_api_call(url, "My API")
