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

from util.register_path import register_path
from util.accounts import registration
from util.login_path import login_path
from util.accounts import login
from util.accounts import logout
from util.accounts import return_user_profile
from util.accounts import user_search
from util.search_path import search_path
from util.settings_path import settings_path
from util.accounts import update_profile
from util.accounts import one_time_password

from util.accounts import auth_github
from util.accounts import auth_callback

from util.avatar_path import avatar_path
from util.accounts import upload_avatar

from util.videotube_path import videotube_path
from util.videotube_path import upload_path
from util.videotube_path import view_video_path

from util.accounts import post_video
from util.accounts import get_all_videos
from util.accounts import get_single_video

from util.accounts import get_transcription
from util.thumbnail_path import thumbnail_path
from util.accounts import change_thumbnail



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

        self.router.add_route("GET", "/register", register_path, True)
        self.router.add_route("POST", "/register", registration, True)

        self.router.add_route("GET", "/login", login_path, True)
        self.router.add_route("POST", "/login", login, True)

        self.router.add_route("GET", "/logout", logout, True)

        self.router.add_route("GET", "/api/users/@me", return_user_profile, True)

        self.router.add_route("GET", "/search-users", search_path, True)
        self.router.add_route("GET", "/api/users/search", user_search, False)

        self.router.add_route("GET", "/settings", settings_path, True)
        self.router.add_route("POST", "/api/users/settings", update_profile, True)


        self.router.add_route("POST", "/api/totp/enable", one_time_password, True)

        #AO2
        self.router.add_route("GET", "/authgithub", auth_github, True)
        self.router.add_route("GET", "/authcallback", auth_callback, False)

        # HW3 LO
        self.router.add_route("GET", "/change-avatar", avatar_path, True)
        self.router.add_route("POST", "/api/users/avatar", upload_avatar, True)

        self.router.add_route("GET", "/videotube", videotube_path, True)
        self.router.add_route("GET", "/videotube/upload", upload_path, True)
        self.router.add_route("GET", "/videotube/videos/", view_video_path, False)

        self.router.add_route("POST", "/api/videos", post_video, True)
        self.router.add_route("GET", "/api/videos", get_all_videos, True)
        self.router.add_route("GET", "/api/videos/", get_single_video, False)

        # HW3 AO1
        self.router.add_route("GET", "/api/transcriptions/", get_transcription, False)

        # HW3 AO2
        self.router.add_route("GET", "/videotube/set-thumbnail", thumbnail_path, False)
        self.router.add_route("PUT", "/api/thumbnails/", change_thumbnail, False)


        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(10000)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        # HW3 code added
        content_length = request.headers.get("Content-Length")
        if content_length:
            content_length = int(content_length.strip())
            while len(request.body) < content_length:
                received_data += self.request.recv(10000)
                request = Request(received_data)

                # request = Request(received_data)

                # I think this last line should be:
                # request.body += received_data
                # since I think Dylan's line would just overwrite the header and that would cause issues with
                # self.router.route_request
            

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
