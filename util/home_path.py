from util.response import Response

def home_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r", encoding="utf-8") as file:
        layout_html = file.read()

    with open("./public/index.html", "r", encoding="utf-8") as file:
        index_html = file.read()
    
    home_page = layout_html.replace("{{content}}", index_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(home_page))
    res.headers(response_headers)

    res.bytes(home_page)

    handler.request.sendall(res.to_data())
    

