from util.response import Response

def settings_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/settings.html", "r") as file:
        settings_html = file.read()

    
    settings_page = layout_html.replace("{{content}}", settings_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(settings_page))
    res.headers(response_headers)

    res.bytes(settings_page)

    handler.request.sendall(res.to_data())
