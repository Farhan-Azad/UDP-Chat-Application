import socket
import select
import sys
import os


def checkKeyboardInput():
    buffer = []
    if os.name == 'nt':  # Windows
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            print(ch, end='', flush=True)
            if ch == '\r':
                print(flush=True)
                buffer.pop()
                line = "".join(buffer)
                buffer.clear()
                return line
            elif ch == '\b':
                if len(buffer) > 0:
                    buffer.pop()
                    line = "".join(buffer)
                    print(f"\r{line}", end='', flush=True)
                    print(f"\r[{line}]", end='', flush=True)
            else:
                buffer.append(ch)
                return None
    return None


class ChatClient:
    def __init__(self, server_ip='127.0.0.1', server_port=20000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = None
        self.buffer = []

    def start(self):
        # Get username
        self.username = input("What's your username? ")

        # Send JOIN message
        join_msg = f"JOIN:{self.username}"
        self.sock.sendto(join_msg.encode('utf-8'), (self.server_ip, self.server_port))

        print(f"\nWelcome {self.username}!")
        print("Commands: users | to <user> msg <message> | to all msg <message> | leave")

        # Main loop
        self.run()

    def run(self):
        while True:
            # Use select on socket with timeout
            ready = select.select([self.sock], [], [], 0.05)

            # Check for incoming messages from server
            if ready[0]:
                data, addr = self.sock.recvfrom(4096)
                message = data.decode('utf-8')
                self.handle_server_message(message)

            # Check for keyboard input
            line = self.check_keyboard()
            if line is not None:
                if not self.handle_user_command(line):
                    break

    def check_keyboard(self):
        if os.name == 'nt':  # Windows
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                print(ch, end='', flush=True)
                if ch == '\r':
                    print()
                    line = "".join(self.buffer)
                    self.buffer.clear()
                    return line
                elif ch == '\b':
                    if len(self.buffer) > 0:
                        self.buffer.pop()
                        # Clear line and reprint
                        print('\b \b', end='', flush=True)
                else:
                    self.buffer.append(ch)
        else:  # Unix/Linux
            import sys
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                rlist, _, _ = select.select([sys.stdin], [], [], 0)
                if rlist:
                    ch = sys.stdin.read(1)
                    if ch == '\n' or ch == '\r':
                        print()
                        line = "".join(self.buffer)
                        self.buffer.clear()
                        return line
                    elif ch == '\x7f':  # backspace
                        if len(self.buffer) > 0:
                            self.buffer.pop()
                            print('\b \b', end='', flush=True)
                    else:
                        self.buffer.append(ch)
                        print(ch, end='', flush=True)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def handle_user_command(self, command):
        command = command.strip()

        if not command:
            return True

        if command == "users":
            # Request user list
            msg = f"USERS:{self.username}"
            self.sock.sendto(msg.encode('utf-8'), (self.server_ip, self.server_port))

        elif command.startswith("to "):
            # Parse message command
            self.send_message(command)

        elif command == "leave":
            # Leave chat
            leave_msg = f"LEAVE:{self.username}"
            self.sock.sendto(leave_msg.encode('utf-8'), (self.server_ip, self.server_port))
            print("Goodbye!")
            return False
        else:
            print("Invalid command!")

        return True

    def send_message(self, command):
        # Parse: to <user1> <user2> ... msg <message>
        # or: to all msg <message>
        parts = command.split(' msg ', 1)
        if len(parts) != 2:
            print("Invalid message format!")
            return

        recipients_part = parts[0][3:].strip()  # Remove "to "
        message_content = parts[1]

        if recipients_part == "all":
            recipients = "all"
        else:
            recipients = ",".join(recipients_part.split())

        # Format: MSG:sender:recipients:message
        msg = f"MSG:{self.username}:{recipients}:{message_content}"
        self.sock.sendto(msg.encode('utf-8'), (self.server_ip, self.server_port))

    def handle_server_message(self, message):
        parts = message.split(':', 1)
        msg_type = parts[0]

        if msg_type == "USERS":
            user_list = parts[1]
            print(f"\nOnline users: {user_list}")

        elif msg_type == "FROM":
            # Incoming message: FROM:sender:content
            rest = parts[1].split(':', 1)
            sender = rest[0]
            content = rest[1]
            print(f"\n{sender}: {content}")

        elif msg_type == "ERROR":
            error_msg = parts[1]
            print(f"\nError message: {error_msg}")


if __name__ == "__main__":
    client = ChatClient()
    client.start()