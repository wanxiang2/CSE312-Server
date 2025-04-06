from util.response import Response

def search_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/search-users.html", "r") as file:
        search_html = file.read()

    
    search_page = layout_html.replace("{{content}}", search_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(search_page))
    res.headers(response_headers)

    res.bytes(search_page)

    handler.request.sendall(res.to_data())