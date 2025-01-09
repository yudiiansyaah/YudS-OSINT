import socket
import concurrent.futures
import streamlit as st


def thread_scan_port(ip, port):
    """Scans a single port for a given IP address using threads."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return port
        return None
    except socket.gaierror as e:
         return {"error": f"Socket error: {e}"}
    except OSError as e:
      if e.errno == 111: # errno 111 is Connection Refused
        return None
      return {"error": f"An OS error occurred: {e}"}
    except Exception as e:
       return {"error": f"An error occurred: {e}"}


def thread_port_scan(ip, start_port, end_port):
    """Scans a range of ports for a given IP address using threads."""
    if not isinstance(start_port, int) or not isinstance(end_port, int) or start_port < 1 or end_port > 65535 or start_port > end_port:
        st.error("Invalid port range.")
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=250) as executor:
        ports = list(range(start_port, end_port + 1))
        results = executor.map(thread_scan_port, [ip] * len(ports), ports)
        open_ports = []
        for result in results:
          if isinstance(result,int):
            open_ports.append(result)
          elif isinstance(result, dict) and "error" in result:
             st.error(result["error"])
        return open_ports