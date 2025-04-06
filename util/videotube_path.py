from util.response import Response

def videotube_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/videotube.html", "r") as file:
        videotube_html = file.read()

    
    videotube_page = layout_html.replace("{{content}}", videotube_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(videotube_page))
    res.headers(response_headers)

    res.bytes(videotube_page)

    handler.request.sendall(res.to_data())


def upload_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/upload.html", "r") as file:
        upload_html = file.read()

    
    upload_page = layout_html.replace("{{content}}", upload_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(upload_page))
    res.headers(response_headers)

    res.bytes(upload_page)

    handler.request.sendall(res.to_data())


def view_video_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    with open("./public/layout/layout.html", "r") as file:
        layout_html = file.read()

    with open("./public/view-video.html", "r") as file:
        view_video_html = file.read()

    
    view_video_page = layout_html.replace("{{content}}", view_video_html).encode()

    response_headers["Content-Type"] = "text/html; charset=UTF-8"
    response_headers["Content-Length"] = str(len(view_video_page))
    res.headers(response_headers)

    res.bytes(view_video_page)

    handler.request.sendall(res.to_data())

