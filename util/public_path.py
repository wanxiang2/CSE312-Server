from util.response import Response
from util.render_404_page import render_404

def public_path(request, handler):
    res = Response()
    response_headers = {}
    request_path = request.path.strip()

    if request_path.endswith(".jpg"):
        with open("." + request_path, "rb") as file:
            image_bits = file.read()

        image_length = len(image_bits)

        response_headers["Content-Type"] = "image/jpeg"
        response_headers["Content-Length"] = str(image_length)
        res.headers(response_headers)

        res.bytes(image_bits)

    elif request_path.endswith(".ico"):
        with open("." + request_path, "rb") as file:
            image_bits = file.read()

        image_length = len(image_bits)

        response_headers["Content-Type"] = "image/x-icon"
        response_headers["Content-Length"] = str(image_length)
        res.headers(response_headers)

        res.bytes(image_bits)

    elif request_path.endswith(".gif"):
        with open("." + request_path, "rb") as file:
            image_bits = file.read()

        image_length = len(image_bits)

        response_headers["Content-Type"] = "image/gif"
        response_headers["Content-Length"] = str(image_length)
        res.headers(response_headers)

        res.bytes(image_bits)

    elif request_path.endswith(".webp"):
        with open("." + request_path, "rb") as file:
            image_bits = file.read()

        image_length = len(image_bits)

        response_headers["Content-Type"] = "image/webp"
        response_headers["Content-Length"] = str(image_length)
        res.headers(response_headers)

        res.bytes(image_bits)

    # This is to be able to host the Dicebear profile pic images. You need this to be
    # able to render the chat user pics.
    elif request_path.endswith(".svg"):
        with open("." + request_path, "rb") as file:
            image_bits = file.read()

        image_length = len(image_bits)

        response_headers["Content-Type"] = "image/svg+xml"
        response_headers["Content-Length"] = str(image_length)
        res.headers(response_headers)

        res.bytes(image_bits)


    elif request_path.endswith(".js"):
        with open("." + request_path, "rb") as file:
            js_bits = file.read()

        js_length = len(js_bits)

        response_headers["Content-Type"] = "text/javascript; charset=UTF-8"
        response_headers["Content-Length"] = str(js_length)
        res.headers(response_headers)

        res.bytes(js_bits)

    elif request_path.endswith(".css"):
        with open("." + request_path, "rb") as file:
            css_bits = file.read()

        css_length = len(css_bits)

        response_headers["Content-Type"] = "text/css; charset=UTF-8"
        response_headers["Content-Length"] = str(css_length)
        res.headers(response_headers)

        res.bytes(css_bits)

    elif request_path.endswith(".html"):
        with open("." + request_path, "rb") as file:
            html_bits = file.read()

        html_length = len(html_bits)

        response_headers["Content-Type"] = "text/html; charset=UTF-8"
        response_headers["Content-Length"] = str(html_length)
        res.headers(response_headers)

        res.bytes(html_bits)

    else:
        #render_404(request, handler)

        res.set_status(404, "Not Found")
        error_body = "404 Not Found"
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)

        res.text(error_body)


    handler.request.sendall(res.to_data())

