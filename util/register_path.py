from util.response import Response

def register_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/register.html", "r") as file:
        register_html = file.read()

    
    register_page = layout_html.replace("{{content}}", register_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(register_page))
    res.headers(response_headers)

    res.bytes(register_page)

    handler.request.sendall(res.to_data())