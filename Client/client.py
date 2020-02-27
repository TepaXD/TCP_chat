import socket
import select
import errno
import sys


# variables
HEADERLEN = 10
#IP = "172.17.0.1"
# 172.17.0.1 is the IP my server docker generated, so in order to connect it has to listen to that IP instead of the regular 127.0.0.1. That is used only if the server and client are running on the same network without a container
PORT = 9000


def main():
    print(f"Welcome to terminal chat!\n")
    myusername = input("Give username: ")
    IP = input("Give room ip (default is 127.0.0.1): ")
    print(
        f"\nYou have connected to {IP}. To update the chat, press ENTER, to leave type /q, to PM someone type @username at the start of the message.\n")
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((IP, PORT))
    clientsocket.setblocking(False)

    encodedusername = myusername.encode("utf-8")
    usernameheader = f"{len(encodedusername):<{HEADERLEN}}".encode("utf-8")
    clientsocket.send(usernameheader + encodedusername)

    while True:
        message = input(f"<{myusername}> ")

        if message:

            message = message.encode("utf-8")
            messageheader = f"{len(message):<{HEADERLEN}}".encode("utf-8")
            clientsocket.send(messageheader + message)

            if message.decode("utf-8") == "/q":
                print("You have left the chat.")
                message = "has left the chat"
                message = message.encode("utf-8")
                messageheader = f"{len(message):<{HEADERLEN}}".encode("utf-8")
                clientsocket.send(messageheader + message)
                sys.exit()

        try:
            while True:
                usernameheader = clientsocket.recv(HEADERLEN)
                if not len(usernameheader):
                    print("Connection closed by the server")
                    sys.exit()

                usernamelen = int(usernameheader.decode("utf-8").strip())
                username = clientsocket.recv(usernamelen).decode("utf-8")

                messageheader = clientsocket.recv(HEADERLEN)
                messagelen = int(messageheader.decode("utf-8").strip())
                message = clientsocket.recv(messagelen).decode("utf-8")

                splitmessage = message.split()
                if message == "has left the chat":
                    print(f"User {username} has left the chat.")

                elif (splitmessage[0][0] == "@") and (splitmessage[0] != "@"+myusername):
                    pass

                elif (splitmessage[0][0] == "@") and (splitmessage[0] == "@"+myusername):
                    message = "PM:"
                    for piece in splitmessage:
                        if piece[0] == "@":
                            continue
                        else:
                            message = message + " " + piece
                            print(f"<{username}> {message}")

                else:
                    print(f"<{username}> {message}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print(str(e))
                sys.exit()
            continue

        except Exception as e:
            print(str(e))
            sys.exit()


main()
