from util.response import Response
from util.render_404_page import render_404

class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        self.routes.append([method.upper(), path, action, exact_path])

    def route_request(self, request, handler):
        method_of_request = request.method
        path_of_request = request.path

        for route in self.routes:
            if method_of_request == route[0]:
                if route[3] == True:
                    if path_of_request == route[1]:
                        route[2](request, handler)
                        return

                else:
                    if path_of_request.startswith(route[1]):
                        route[2](request, handler)
                        return
                    

        #render_404(request, handler)
                    
        not_found_response = "HTTP/1.1 404 Not Found\r\n"
        not_found_response = not_found_response + "Content-Type: text/plain;charset=utf-8\r\n"
        not_found_response = not_found_response + "Content-Length:13\r\n"
        not_found_response = not_found_response + "X-Content-Type-Options:nosniff\r\n\r\n"
        not_found_response = not_found_response + "404 Not Found"
        not_found_response = not_found_response.encode()
        handler.request.sendall(not_found_response)








        # res = Response()
        # response_headers = {}

        # with open("./public/layout/layout.html", "r", encoding="utf-8") as file:
        #     layout_html = file.read()

        # with open("./public/404.html", "r", encoding="utf-8") as file:
        #     html_404 = file.read()

        # page_404 = layout_html.replace("{{content}}", html_404).encode()

        # res.set_status(404, "Not Found")

        # response_headers["Content-Type"] = "text/html; charset=UTF-8"
        # response_headers["Content-Length"] = str(len(page_404))
        # res.headers(response_headers)

        # res.bytes(page_404)

        # handler.request.sendall(res.to_data())






