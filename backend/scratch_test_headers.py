import socket

def send_raw_options(origin):
    raw_request = (
        f"OPTIONS /auth/login HTTP/1.1\r\n"
        f"Host: 127.0.0.1:8000\r\n"
        f"User-Agent: Mozilla/5.0\r\n"
        f"Accept: */*\r\n"
        f"Access-Control-Request-Method: POST\r\n"
        f"Access-Control-Request-Headers: authorization,content-type\r\n"
        f"Origin: {origin}\r\n"
        f"Connection: close\r\n\r\n"
    )
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 8000))
    s.sendall(raw_request.encode())
    
    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data
    s.close()
    return response.decode()

print("Testing with http://localhost:5173:")
print(send_raw_options("http://localhost:5173"))

print("\nTesting with http://127.0.0.1:5173:")
print(send_raw_options("http://127.0.0.1:5173"))
