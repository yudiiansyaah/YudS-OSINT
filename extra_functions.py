import re
from bs4 import BeautifulSoup
import requests
import streamlit as st

def phone_number_lookup(query):
    """Attempts to find phone numbers in a given query or on a website.
    Regex pattern for a common formats, adapt as needed
    """

    if not query:
        return {"message": "No query provided for phone number lookup"}
    phone_number_regex = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{1,4}\)?[-.\s]?)?(\d{1,4}[-.\s]?\d{1,9})')
    numbers = []
    if query.startswith('http'): # check if the query is a URL
       try:
           response = requests.get(query,timeout=5)
           response.raise_for_status()
           soup = BeautifulSoup(response.content, 'html.parser')
           text = soup.get_text() # extract all text
           for match in phone_number_regex.finditer(text):
               numbers.append(match.group().strip()) # append non-empty matches
       except requests.exceptions.RequestException as e:
          return {"error": f"Error accessing webpage {query}: {e}"}

    elif isinstance(query,str):
      for match in phone_number_regex.finditer(query):
        numbers.append(match.group().strip())

    if numbers:
        return list(set(numbers)) # return unique phone numbers
    return {"message": "No phone numbers detected"}



def email_lookup(query):
     """Attempts to find email addresses in given query or webpage"""
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


def technology_detection(url):
    """Detects technologies based on HTTP headers and HTML patterns."""
    if not url:
       return {"error": "URL cannot be empty."}
    with st.spinner(f"Detecting Technologies for {url}"):
        try:
            response = requests.get(url, timeout = 5)
            response.raise_for_status()
            tech = {"headers" : {}, "html_patterns" : []}

            # header analysis
            if 'Server' in response.headers:
                tech["headers"]["Server"] = response.headers['Server']
            else:
                tech["headers"]["Server"] = "Not Found"
            # html patterns
            soup = BeautifulSoup(response.content, 'html.parser')
            if soup.find(attrs={"id": "wpadminbar"}) :
                tech["html_patterns"].append("Wordpress")
            if soup.find("meta", attrs={"name": "generator"}) and "Joomla" in  soup.find("meta", attrs={"name": "generator"})["content"]:
                tech["html_patterns"].append("Joomla")
            if not tech["html_patterns"]:
                tech["html_patterns"].append("None")
            return tech
        except requests.exceptions.RequestException as e:
            return {"error": f"Error during tech detection: {e}"}


def os_detection(url):
  """Attempt OS detection from user agent header"""
  if not url:
       return {"error": "URL cannot be empty."}
  with st.spinner(f"Detecting OS for {url}"):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        user_agent = response.request.headers.get('User-Agent')
        if user_agent:
            os_match = re.search(r'\(([^;)]+)', user_agent)
            if os_match:
               return os_match.group(1)
            else:
               return "Operating system information not detected"
        else:
            return "No User-Agent header found."
    except requests.exceptions.RequestException as e:
          return {"error": f"Error during OS Detection {e}"}


def gather_domain_info(url):
    """Gathers additional info from the target URL like robots.txt or social media"""
    if not url:
       return {"error": "URL cannot be empty."}
    with st.spinner(f"Gathering domain info for {url}"):
        try:
           domain_info = {}
           response = requests.get(url, timeout=5)
           response.raise_for_status()
           soup = BeautifulSoup(response.content, 'html.parser')

           # find social media links
           social_media_links = []
           social_patterns = re.compile(r"(facebook|twitter|instagram|linkedin|youtube)\.com")
           for link in soup.find_all('a', href=True):
                if social_patterns.search(link['href']):
                    social_media_links.append(link['href'])
           domain_info['social_media'] = list(set(social_media_links))

           # check robots.txt
           try:
               robots_url = url.rstrip('/') + "/robots.txt"
               robots_response = requests.get(robots_url,timeout=5)
               if robots_response.status_code == 200:
                  domain_info['robots_txt'] = robots_response.text
               else:
                   domain_info['robots_txt'] = "robots.txt not found"
           except requests.exceptions.RequestException as e:
                domain_info['robots_txt'] = "robots.txt error"
           return domain_info

        except requests.exceptions.RequestException as e:
              return {"error" : f"Error accessing webpage: {e}"}