from util.response import Response

def render_404(request, handler):
    res = Response()
    response_headers = {}

    with open("./public/layout/layout.html", "r", encoding="utf-8") as file:
        layout_html = file.read()

    with open("./public/404.html", "r", encoding="utf-8") as file:
        html_404 = file.read()

    page_404 = layout_html.replace("{{content}}", html_404).encode()

    res.set_status(404, "Not Found")

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    
    res.headers(response_headers)

    res.bytes(page_404)

    handler.request.sendall(res.to_data())
