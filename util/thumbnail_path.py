from util.response import Response

def thumbnail_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/set-thumbnail.html", "r") as file:
        thumbnail_html = file.read()

    
    thumbnail_page = layout_html.replace("{{content}}", thumbnail_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(thumbnail_page))
    res.headers(response_headers)

    res.bytes(thumbnail_page)

    handler.request.sendall(res.to_data())