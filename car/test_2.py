import asyncio
import socket
import psutil

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection('10.0.1.1', 12345, loop=loop)
    print(f'Send: {message}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()}')

    print('Close the connection')
    writer.close()

async def send_messages():
    while True:
        if check_connection():
            try:
                message = "Hello World!"
                loop = asyncio.get_running_loop()
                await tcp_echo_client(message, loop)
            except Exception as e:
                print(f"Failed to send message: {e}")
        else:
            print("Ethernet Disconnected")
        await asyncio.sleep(5)

asyncio.run(send_messages())
