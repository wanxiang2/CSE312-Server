import json

class Response:
    def __init__(self):
        self.response_line = b"HTTP/1.1 200 OK\r\n"
        self.response_headers = b""
        self.reponse_body = b"\r\n"

    def set_status(self, code, text):
        status = "HTTP/1.1 " + str(code) + " "  + text
        self.response_line = status.encode()
        return self

    def headers(self, headers):
        next_header = ""
        for key, value in headers:
            next_header = next_header + key + ": " + value + "\r\n"

        self.response_headers = next_header.encode()
        return self

    def cookies(self, cookies):
        pass

    def bytes(self, data):
        self.reponse_body = self.reponse_body + data
        return self

    def text(self, data):
        self.reponse_body = self.reponse_body + data.encode()
        return self

    def json(self, data):
        pass

    def to_data(self):
        return self.response_line + self.response_headers + self.reponse_body
