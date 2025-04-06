from util.response import Response

def avatar_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/change-avatar.html", "r") as file:
        avatar_html = file.read()

    
    avatar_page = layout_html.replace("{{content}}", avatar_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(avatar_page))
    res.headers(response_headers)

    res.bytes(avatar_page)

    handler.request.sendall(res.to_data())
