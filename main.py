import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
import os
import time
import schedule
import json
import requests

from core_functions import whois_lookup, dns_lookup
from async_utils import async_port_scan, get_neon_loading_animation
from thread_utils import thread_port_scan
from utils import get_geolocation
from extra_functions import technology_detection, os_detection, gather_domain_info
from api_integration import shodan_lookup, virustotal_lookup, my_api_whois, my_api_geoip, my_api_ssl, my_api_phone, my_api_email

# External API functions and integrations:
def subdomain_lookup(domain):
    """Enumerates subdomains for a given domain using crt.sh."""
    if not domain:
        return {"error": "Domain cannot be empty."}
    with st.spinner(f"Enumerating subdomains for {domain}"):
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            subdomains = [entry['name_value'] for entry in response.json()]
            return list(set(subdomains))
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching subdomains: {e}"}
        except json.JSONDecodeError as e:
           return {"error": f"Error decoding JSON: {e}"}


# Data handling and visualization
def visualize_ports(ports, start_port, end_port):
    """Visualizes port scan results using Plotly."""
    if not ports:
        return None  # Return None if there are no ports
    with st.spinner("Visualizing port data"):
        all_ports = list(range(start_port, end_port + 1))
        port_status = [1 if port in ports else 0 for port in all_ports]

        fig = go.Figure(data=[go.Bar(x=all_ports,
                                     y=port_status,
                                     marker_color=['lime' if status == 1 else 'red' for status in port_status]
                                     )
                             ])
        fig.update_layout(
            title='Open Port Scan Results',
            xaxis_title='Ports',
            yaxis_title='Status',
            showlegend=False,
            hovermode=False,
            dragmode=False,
        )
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True, showticklabels=False)
        return fig


def format_port_output(ports):
    """Formats open port list for display in the UI."""
    if not ports:
        return "<p>No open ports found</p>"
    output = "<p>Open Ports: "
    colored_ports = [f'<span style="color:lime;">{port}</span>' for port in ports]
    output += ", ".join(colored_ports)
    output += "</p>"
    return output


def create_pandas_dataframe(data):
    """Creates a pandas DataFrame from given data."""
    if not data:
        return None
    with st.spinner("Creating Dataframe"):
        return pd.DataFrame(data)


def generate_report(data, filename):
    """Generates a PDF report from given data."""
    if not data:
       return {"error": "No Data to be exported"}
    with st.spinner(f"Generating PDF report as {filename}"):
        try:
            pdf = canvas.Canvas(filename)
            pdf.setTitle("OSINT Report")
            pdf.drawString(100, 800, "OSINT Report")

            y = 780
            for key, value in data.items():
                if isinstance(value, dict):
                    pdf.drawString(100, y, f"{key}: ")
                    y -= 15
                    for k, v in value.items():
                        pdf.drawString(120, y, f"{k}: {v}")
                        y -= 15
                elif isinstance(value, list):
                    pdf.drawString(100, y, f"{key}: ")
                    y -= 15
                    for item in value:
                        pdf.drawString(120, y, f"- {item}")
                        y -= 15
                else:
                    pdf.drawString(100, y, f"{key}: {value}")
                    y -= 20

            pdf.save()
            return f"Report saved as {filename}"

        except Exception as e:
            return {"error": f"Error generating report: {e}"}

# Main app functionality
st.markdown(
    """
    <style>
        .title-center {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title-center" style="color:#39FF14;">OSINT (Open Source Intelligence)</h1>', unsafe_allow_html=True)

st.markdown(
    """
    <style>
        .created-by {
            margin-left: 0;
            padding-left: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(''' <h1 class="created-by"><span style="color:#E10600;">Created</span> <span style="color:#FFA400;">By</span> <span style="color:#FFE900;">Yud'S</span></h1>''',
            unsafe_allow_html=True)


domain = st.text_input('Enter domain for analysis or ip address:')

if domain:
    # Tab Layout
    tab1, tab2, tab3 = st.tabs(["Domain/IP Info", "Extra Info", "Export"])

    with tab1:
        # --- WHOIS ---
        st.subheader("WHOIS Lookup")
        whois_data = whois_lookup(domain)
        if "error" in whois_data:
            st.error(whois_data["error"])
        else:
            st.json(whois_data)
        # --- WHOIS from My API ---
        st.subheader("WHOIS Lookup (My API)")
        my_api_whois_data = my_api_whois(domain)
        if "error" in my_api_whois_data:
            st.error(my_api_whois_data["error"])
        else:
            st.json(my_api_whois_data)

        # --- DNS Lookup ---
        st.subheader("DNS Lookup")
        dns_data = dns_lookup(domain)
        if "error" in dns_data:
            st.error(dns_data["error"])
        else:
            st.write(dns_data)

        # --- Subdomains ---
        st.subheader("Subdomain Enumeration")
        subdomains = subdomain_lookup(domain)
        if "error" in subdomains:
            st.error(subdomains["error"])
        else:
            st.write(subdomains)

        # --- SSL Info ---
        st.subheader("SSL Certificate Information")
        ssl_info = my_api_ssl(domain)
        if "error" in ssl_info:
            st.error(ssl_info["error"])
        else:
            st.json(ssl_info)

        if isinstance(dns_data, list):
            for ip in dns_data:
                # --- Geolocation ---
                st.subheader(f"Geolocation for {ip}")
                geo_data = get_geolocation(ip)
                if "error" in geo_data:
                    st.error(geo_data["error"])
                else:
                    st.json(geo_data)

                # --- Geolocation from My API ---
                st.subheader(f"Geolocation (My API) for {ip}")
                my_api_geo_data = my_api_geoip(ip)
                if "error" in my_api_geo_data:
                   st.error(my_api_geo_data["error"])
                else:
                   st.json(my_api_geo_data)

                # --- Shodan Lookup ---
                st.subheader(f"Shodan Lookup for {ip}")
                shodan_data = shodan_lookup(ip)
                if "error" in shodan_data:
                    st.error(shodan_data["error"])
                else:
                    st.json(shodan_data)

                # --- Port Scan ---
                st.subheader(f"Port Scan for {ip}")
                start_port = 1
                end_port = 65535
                progress_bar_placeholder = st.empty()
                def progress_callback(progress):
                    animation_html = get_neon_loading_animation(progress)
                    progress_bar_placeholder.markdown(animation_html, unsafe_allow_html=True)
                ports = asyncio.run(async_port_scan(ip, start_port, end_port, progress_callback=progress_callback))  # Use the async scan
                progress_bar_placeholder.empty()
                # Format and display open ports with colored text
                formatted_output = format_port_output(ports)
                st.markdown(formatted_output, unsafe_allow_html=True)

                fig = visualize_ports(ports, start_port, end_port)
                if fig: # only render if port data available
                    st.plotly_chart(fig, key=ip)
    with tab2:
        # Automatically gather phone numbers and emails if the domain is a URL
        if domain.startswith("http"):
            st.subheader("Auto Phone Number OSINT")
            phone_data = my_api_phone(domain)
            if "error" in phone_data:
                st.error(phone_data["error"])
            elif "message" in phone_data:
                st.write(phone_data["message"])
            else:
              st.write(phone_data)
            st.subheader("Auto Email OSINT")
            email_data = my_api_email(domain)
            if "error" in email_data:
                st.error(email_data["error"])
            elif "message" in email_data:
                st.write(email_data["message"])
            else:
                st.write(email_data)

            # --- Technology Detection ---
            st.subheader("Technology Detection")
            tech_data = technology_detection(domain)
            if "error" in tech_data:
                st.error(tech_data["error"])
            else:
                st.json(tech_data)

            # --- OS Detection ---
            st.subheader("Operating System Detection")
            os_info = os_detection(domain)
            if "error" in os_info:
                st.error(os_info["error"])
            else:
                st.write(os_info)

            # --- Domain Information Gathering ---
            st.subheader("Domain Information Gathering")
            domain_extra_info = gather_domain_info(domain)
            if "error" in domain_extra_info:
                st.error(domain_extra_info["error"])
            else:
                st.json(domain_extra_info)

            # --- VirusTotal Lookup ---
            st.subheader("VirusTotal Lookup")
            virustotal_data = virustotal_lookup(domain)
            if "error" in virustotal_data:
                st.error(virustotal_data["error"])
            else:
                st.json(virustotal_data)

    with tab3:
       # --- Export Options ---
        st.subheader("Export Data")
        if st.button("Generate Report"):
            report_data = {
                "WHOIS": whois_data,
                "WHOIS (My API)" : my_api_whois_data,
                "Subdomains": subdomains,
                "SSL Info": ssl_info,
                "DNS Data": dns_data,
            }
            if isinstance(dns_data, list):
                for ip in dns_data:
                    geo_data = get_geolocation(ip)
                    if isinstance(geo_data, dict):
                        report_data[f"Geolocation for {ip}"] = geo_data
                    my_api_geo_data = my_api_geoip(ip)
                    if isinstance(my_api_geo_data,dict):
                      report_data[f"Geolocation (My API) for {ip}"] = my_api_geo_data
                    shodan_data = shodan_lookup(ip)
                    if isinstance(shodan_data,dict):
                        report_data[f"Shodan Data for {ip}"] = shodan_data
                    ports = asyncio.run(async_port_scan(ip, 1, 1024))
                    if ports:
                        report_data[f"Open Ports for {ip}"] = ports
            if domain.startswith('http'):
                report_data["Phone Number"] = phone_data
                report_data["Emails"] = email_data
                report_data["Technology Info"] = tech_data
                report_data["Operating System"] = os_info
                report_data["Extra Domain Info"] = domain_extra_info
                report_data["Virus Total Info"] = virustotal_data

            report_path = generate_report(report_data, "OSINT_Report.pdf")
            if "error" in report_path:
              st.error(report_path["error"])
            else:
                st.success(report_path)

        if st.checkbox("Export to CSV"):
                full_data = []
                if isinstance(dns_data, list):
                    for ip in dns_data:
                        geo_data = get_geolocation(ip)
                        my_api_geo_data = my_api_geoip(ip)
                        shodan_data = shodan_lookup(ip)
                        ports = asyncio.run(async_port_scan(ip, 1, 1024))
                        data_for_df = {
                            "Domain": domain,
                            "IP": ip,
                            "WHOIS": whois_data,
                            "WHOIS (My API)" : my_api_whois_data,
                            "Subdomains": subdomains,
                            "SSL Info": ssl_info,
                            "DNS Data": dns_data,
                            "Geolocation": geo_data,
                            "Geolocation (My API)" : my_api_geo_data,
                            "Shodan Data" : shodan_data,
                            "Open Ports": ports,
                        }
                        full_data.append(data_for_df)
                else:
                  data_for_df = {
                            "Domain": domain,
                            "WHOIS": whois_data,
                            "WHOIS (My API)" : my_api_whois_data,
                            "Subdomains": subdomains,
                            "SSL Info": ssl_info,
                            "DNS Data": dns_data,
                        }
                  full_data.append(data_for_df)
                if domain.startswith('http'):
                    for data_dic in full_data:
                        data_dic["Phone Number"] = phone_data
                        data_dic["Emails"] = email_data
                        data_dic["Technology Info"] = tech_data
                        data_dic["Operating System"] = os_info
                        data_dic["Extra Domain Info"] = domain_extra_info
                        data_dic["Virus Total Info"] = virustotal_data

                df = create_pandas_dataframe(full_data)
                if df is not None:
                  st.download_button(
                      label="Download CSV",
                      data=df.to_csv(index=False).encode("utf-8"),
                      file_name=f"OSINT_Data_{domain}.csv",
                      mime="text/csv",
                      )


    # --- Configuration ---
    if st.checkbox("Show Configuration Options"):
        st.subheader("Configuration")
        st.write(
            "Here you could customize things like scheduling tasks, saving API keys securely, notification settings, etc. This is a work in progress! :D")


# --- Automated Task (Example) ---
def automated_task():
    print("Running scheduled task...")


schedule.every().day.at("00:00").do(automated_task)

while True:
    schedule.run_pending()
    time.sleep(1)
