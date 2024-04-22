import asyncio
import socket
import psutil

from config import *

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected to {addr}")
    while True:
        data = await reader.read(100)
        if not data:
            print(f"Disconnected from {addr}")
            break
        message = data.decode()
        print(f"Received from {addr}: {message}")
        # Simulate sending a response or other processing
        writer.write(f"Echo: {message}".encode())
        await writer.drain()
    writer.close()

async def main_server():
    server = await asyncio.start_server(handle_client, CHARGER_IP, CHARGER_IP)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

async def check_and_run_server():
    while True:
        if check_connection():
            await main_server()
        else:
            print("Ethernet Disconnected")
        await asyncio.sleep(1)

asyncio.run(check_and_run_server())
