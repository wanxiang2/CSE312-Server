import socketserver
from util.request import Request
from util.router import Router
from util.hello_path import hello_path

from util.public_path import public_path
from util.home_path import home_path
from util.chat_path import chat_path
from util.api import create_message
from util.api import get_message
from util.api import update_message
from util.api import delete_message
from util.api import add_emoji
from util.api import remove_emoji
from util.api import nickname



class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)

        # TODO: Add your routes here
        self.router.add_route("GET", "/public", public_path, False)

        self.router.add_route("GET", "/", home_path, True)
        self.router.add_route("GET", "/chat", chat_path, True)

        self.router.add_route("POST", "/api/chats", create_message, True)
        self.router.add_route("GET", "/api/chats", get_message, True)
        self.router.add_route("PATCH", "/api/chats/", update_message, False)
        self.router.add_route("DELETE", "/api/chats/", delete_message, False)

        self.router.add_route("PATCH", "/api/reaction/", add_emoji, False)
        self.router.add_route("DELETE", "/api/reaction/", remove_emoji, False)

        self.router.add_route("PATCH", "/api/nickname", nickname, True)


        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
