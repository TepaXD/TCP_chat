import socket
import select

# variables
HEADERLEN = 10
IP = socket.gethostname()
PORT = 9000

# setting the server up
servsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

servsocket.bind(('', PORT))

servsocket.listen(10)

socketlist = [servsocket]
clients = {}

print(f"Listening connections on {IP}:{PORT}...")


def receive_message(clientsocket):
    try:
        messageheader = clientsocket.recv(HEADERLEN)

        if not len(messageheader):
            return False

        messagelen = int(messageheader.decode("utf-8").strip())
        return {"header": messageheader, "data": clientsocket.recv(messagelen)}

    except:
        return False


def main():
    while True:
        readsockets, _, exceptionsockets = select.select(
            socketlist, [], socketlist)

        for notifiedsocket in readsockets:
            if notifiedsocket == servsocket:
                clientsocket, clientaddress = servsocket.accept()

                user = receive_message(clientsocket)
                if user is False:
                    continue

                socketlist.append(clientsocket)

                clients[clientsocket] = user

                print(
                    f"Accepted new connection from {clientaddress[0]}:{clientaddress[1]} username:{user['data'].decode('utf-8')}")

            else:
                message = receive_message(notifiedsocket)

                if message and message['data'].decode("utf-8") == '/q':

                    print(
                        f"Closed connection from {clients[notifiedsocket]['data'].decode('utf-8')}")
                    message = receive_message(notifiedsocket)

                    for clientsocket in clients:
                        if clientsocket != notifiedsocket:
                            clientsocket.send(
                                user['header'] + user['data'] + message['header'] + message['data'])
                    socketlist.remove(notifiedsocket)
                    continue

                user = clients[notifiedsocket]

                if message:
                    print(
                        f"Recieved message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

                    for clientsocket in clients:
                        if clientsocket != notifiedsocket:
                            clientsocket.send(
                                user['header'] + user['data'] + message['header'] + message['data'])

        for notifiedsocket in exceptionsockets:
            socketlist.remove(notifiedsocket)
            del clients[notifiedsocket]


main()
