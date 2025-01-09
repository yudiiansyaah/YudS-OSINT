import whois
import dns.resolver
import requests
import ssl
import socket
from OpenSSL import crypto
import streamlit as st


def whois_lookup(domain):
    """Retrieves WHOIS information for a given domain."""
    if not domain:
        return {"error": "Domain cannot be empty."}
    with st.spinner(f"Retrieving WHOIS data for {domain}"):
        try:
            w = whois.whois(domain)
            if w.domain_name is None:
                return {"error": f"Error retrieving WHOIS data: Domain {domain} not found"}
            return w
        except whois.parser.PywhoisError:
            return {"error": f"Error retrieving WHOIS data: Domain {domain} not found"}
        except Exception as e:
            return {"error": f"Error retrieving WHOIS data: {e}"}


def dns_lookup(domain):
    """Resolves DNS records (A records) for a given domain."""
    if not domain:
      return {"error": "Domain cannot be empty."}
    with st.spinner(f"Resolving DNS for {domain}"):
        try:
            result = dns.resolver.resolve(domain, 'A')
            ips = [ipval.to_text() for ipval in result]
            return ips
        except dns.resolver.NoAnswer as e:
           return {"error": f"Error resolving DNS for {domain}: No answer record found"}
        except dns.resolver.NXDOMAIN as e:
            return {"error": f"Error resolving DNS for {domain}: Domain does not exist"}
        except Exception as e:
            return {"error": f"Error resolving DNS for {domain}: {e}"}

def ssl_certificate_info(domain):
    """Retrieves SSL certificate information for a given domain."""
    if not domain:
      return {"error": "Domain cannot be empty."}
    with st.spinner(f"Retrieving SSL certificate information for {domain}"):
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