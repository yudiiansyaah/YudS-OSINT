import socket
import asyncio
import streamlit as st
import random
import math

def get_neon_loading_animation(progress):
    hue = int((progress * 360 * 3) % 360)
    return f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <div style="width: 50px; height: 50px; border-radius: 50%; position: relative;">
            <div style="width: 100%; height: 100%;
                        background: conic-gradient(
                            from 0deg,
                            hsl({int(hue)}, 100%, 50%) 0%,
                            hsl({int(hue + 360/3)}, 100%, 50%) 33.33%,
                            hsl({int(hue + 360/3*2)}, 100%, 50%) 66.66%,
                            hsl({int(hue)}, 100%, 50%) 100%
                        );
                        border-radius: 50%;
                        animation: rotate 2s linear infinite;
                        ">
            </div>
            </div>
            <style>
                @keyframes rotate {{
                   from {{ transform: rotate(0deg); }}
                   to   {{ transform: rotate(360deg); }}
                }}
            </style>
    </div>
    """


async def async_scan_port(ip, port):
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
      if e.errno == 111: 
        return None
      return {"error": f"An OS error occurred: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


async def async_port_scan(ip, start_port, end_port, progress_callback=None):
    if not isinstance(start_port, int) or not isinstance(end_port, int) or start_port < 1 or end_port > 65535 or start_port > end_port:
        st.error("Invalid port range.")
        return []

    total_ports = end_port - start_port + 1
    tasks = []
    open_ports = []

    for port in range(start_port, end_port + 1):
        task = asyncio.create_task(async_scan_port(ip, port))
        tasks.append(task)
        if progress_callback:
          progress_callback((port - start_port + 1) / total_ports)

    for task in tasks:
        result = await task
        if isinstance(result, int):
            open_ports.append(result)
        elif isinstance(result, dict) and "error" in result:
            st.error(result["error"])  

    return open_ports
