import requests
import streamlit as st
import json

def get_geolocation(ip):
    if not ip:
        return {"error": "IP Address cannot be empty."}
    with st.spinner(f"Getting geolocation for {ip}"):
        url = f"http://ip-api.com/json/{ip}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API error: {e}"}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
