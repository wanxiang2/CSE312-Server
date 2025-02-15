from util.response import Response

def chat_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/chat.html", "r") as file:
        chat_html = file.read()

    
    chat_page = layout_html.replace("{{content}}", chat_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(chat_page))
    res.headers(response_headers)

    res.bytes(chat_page)

    handler.request.sendall(res.to_data())



