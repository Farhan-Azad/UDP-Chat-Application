import socket
import sys


class ChatServer:
    def __init__(self, port=20000):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = {}  # username -> (ip, port)

    def start(self):
        self.sock.bind(('127.0.0.1', self.port))
        print(f"Server started on port {self.port}")
        print("Waiting for clients...")

        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                message = data.decode('utf-8')
                self.handle_message(message, addr)
            except Exception as e:
                print(f"Error: {e}")

    def handle_message(self, message, addr):
        parts = message.split(':', 2)
        msg_type = parts[0]

        if msg_type == "JOIN":
            username = parts[1]
            self.clients[username] = addr
            print(f"{username} joined from {addr}")

        elif msg_type == "LEAVE":
            username = parts[1]
            if username in self.clients:
                del self.clients[username]
                print(f"{username} left the chat")

        elif msg_type == "USERS":
            username = parts[1]
            user_list = ", ".join(self.clients.keys())
            response = f"USERS:{user_list}"
            self.sock.sendto(response.encode('utf-8'), addr)

        elif msg_type == "MSG":
            # Format: MSG:sender:recipients:message
            sender = parts[1]
            rest = parts[2].split(':', 1)
            recipients = rest[0].split(',')
            msg_content = rest[1]

            # Check if "all" is recipient
            if recipients[0] == "all":
                # Send to everyone except sender
                for username, client_addr in self.clients.items():
                    if username != sender:
                        forward_msg = f"FROM:{sender}:{msg_content}"
                        self.sock.sendto(forward_msg.encode('utf-8'), client_addr)
            else:
                # Send to specific recipients
                for recipient in recipients:
                    recipient = recipient.strip()

                    # Don't send message back to sender
                    if recipient == sender:
                        continue

                    if recipient in self.clients:
                        forward_msg = f"FROM:{sender}:{msg_content}"
                        self.sock.sendto(forward_msg.encode('utf-8'), self.clients[recipient])
                    else:
                        # Recipient not online
                        error_msg = f"ERROR:<{recipient} is not online!>"
                        self.sock.sendto(error_msg.encode('utf-8'), addr)


if __name__ == "__main__":
    server = ChatServer()
    server.start()