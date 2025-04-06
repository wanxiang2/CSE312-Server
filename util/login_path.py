from util.response import Response

def login_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/login.html", "r") as file:
        login_html = file.read()

    
    login_page = layout_html.replace("{{content}}", login_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(login_page))
    res.headers(response_headers)

    res.bytes(login_page)

    handler.request.sendall(res.to_data())
