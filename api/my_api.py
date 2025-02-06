# api/my_api.py
from fastapi import FastAPI, HTTPException
from whois import whois
import socket
import requests
import json
import re
from bs4 import BeautifulSoup
import ssl
from OpenSSL import crypto

app = FastAPI()

def get_geolocation(ip):
    if not ip:
        return {"error": "IP Address cannot be empty."}
    url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API error: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Error decoding JSON: {e}"}


def get_ssl_certificate_info(domain):
    if not domain:
      return {"error": "Domain cannot be empty."}
    try:
        conn = socket.create_connection((domain, 443), timeout=5)
        context = ssl.create_default_context()
        sock = context.wrap_socket(conn, server_hostname=domain)
        cert = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

        issuer_components = x509.get_issuer().get_components()
        subject_components = x509.get_subject().get_components()

        issuer = {}
        subject = {}

        if isinstance(issuer_components, tuple):
           try:
              issuer = {k.decode(): v.decode() for k, v in issuer_components}
           except:
             issuer = {"Error" : "Failed to Decode"}
        elif isinstance(issuer_components, dict):
           try:
               issuer = {k.decode(): v.decode() for k, v in issuer_components.items()}
           except:
               issuer = {"Error" : "Failed to Decode"}
        else:
           issuer = {"Error" : "Issuer components is not a dictionary or tuple"}

        if isinstance(subject_components, tuple):
           try:
               subject = {k.decode(): v.decode() for k, v in subject_components}
           except:
               subject = {"Error" : "Failed to Decode"}
        elif isinstance(subject_components, dict):
            try:
                subject = {k.decode(): v.decode() for k, v in subject_components.items()}
            except:
                subject = {"Error" : "Failed to Decode"}
        else:
           subject = {"Error": "Subject components is not a dictionary or tuple"}

        return {
              "Issuer": issuer,
              "Subject": subject,
              "Version": x509.get_version(),
              "Serial Number": x509.get_serial_number(),
            }
    except socket.timeout:
       return {"error" : "Connection timed out while retrieving SSL certificate"}
    except Exception as e:
        return {"error": f"Error retrieving SSL certificate: {e}"}

def get_phone_number_lookup(query):
    if not query:
        return {"message": "No query provided for phone number lookup"}
    phone_number_regex = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{1,4}\)?[-.\s]?)?(\d{1,4}[-.\s]?\d{1,9})')
    numbers = []
    if query.startswith('http'):
       try:
           response = requests.get(query,timeout=5)
           response.raise_for_status()
           soup = BeautifulSoup(response.content, 'html.parser')
           text = soup.get_text() 
           for match in phone_number_regex.finditer(text):
               numbers.append(match.group().strip()) 
       except requests.exceptions.RequestException as e:
          return {"error": f"Error accessing webpage {query}: {e}"}

    elif isinstance(query,str):
      for match in phone_number_regex.finditer(query):
        numbers.append(match.group().strip())
    if numbers:
        return list(set(numbers)) 
    return {"message": "No phone numbers detected"}



def get_email_lookup(query):
     if not query:
         return {"message": "No query provided for email lookup"}
     email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
     emails = []
     if query.startswith('http'):
         try:
            response = requests.get(query, timeout =5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            for match in email_regex.finditer(text):
                emails.append(match.group().strip())
         except requests.exceptions.RequestException as e:
          return {"error" : f"Error accessing webpage {query}: {e}"}

     elif isinstance(query,str):
      for match in email_regex.finditer(query):
        emails.append(match.group().strip())

     if emails:
        return list(set(emails))
     return {"message" : "No emails detected"}

@app.get("/whois/{domain}")
async def read_whois(domain: str):
    try:
        w = whois(domain)
        if w.domain_name is None:
            raise HTTPException(status_code=404, detail="Domain not found")
        return w.__dict__
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/geoip/{ip}")
async def read_geoip(ip: str):
    try:
       geo_data = get_geolocation(ip)
       if "error" in geo_data:
            raise HTTPException(status_code=400, detail=geo_data["error"])
       return geo_data
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/ssl/{domain}")
async def read_ssl(domain: str):
    try:
       ssl_data = get_ssl_certificate_info(domain)
       if "error" in ssl_data:
         raise HTTPException(status_code=400, detail=ssl_data["error"])
       return ssl_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/phone/{query}")
async def read_phone_lookup(query: str):
    try:
        phone_data = get_phone_number_lookup(query)
        if "error" in phone_data:
             raise HTTPException(status_code=400, detail=phone_data["error"])
        return phone_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/email/{query}")
async def read_email_lookup(query: str):
  try:
     email_data = get_email_lookup(query)
     if "error" in email_data:
         raise HTTPException(status_code=400, detail=email_data["error"])
     return email_data
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error: {e}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
