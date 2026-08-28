UDP CHAT APPLICATION
- Farhan Azad


Files:
- chat_server.py: The centralized chat server
- chat_client.py: The chat client application



How to Run:

1. Start the server first:
   python chat_server.py

2. In separate terminal windows, start multiple clients:
   python chat_client.py

3. When prompted, enter a username for each client (e.g., alice, bob, joe, jill)



Commands:

users
    - Lists all online users

to <username> msg <message>
    - Send a message to a single user
    - Example: to bob msg Hi Bob!

to <user1> <user2> ... msg <message>
    - Send a message to multiple users
    - Example: to bob joe msg Hi guys!

to all msg <message>
    - Broadcast a message to all users except yourself
    - Example: to all msg Hello everyone!

leave
    - Exit the chat application



Protocol Design:

Client -> Server Messages:
- JOIN:username
- LEAVE:username
- USERS:username
- MSG:sender:recipients:message_content

Server -> Client Messages:
- USERS:user1,user2,user3,...
- FROM:sender:message_content
- ERROR:error_message



Key Features:

- UDP socket on port 20000
- Non-blocking I/O using select() with 50ms timeout
- Windows-compatible keyboard polling using msvcrt
- Server tracks online users and routes messages
- Error handling for offline recipients
- Messages not echoed back to sender



Testing Notes:

- All clients and server run on localhost (127.0.0.1)
- No packet loss on loopback interface
- Single-threaded client design
- Commands assumed to be entered without errors
- Each user joins from only one client

Watch the demo video: https://www.youtube.com/watch?v=9NKhHAVH7gc