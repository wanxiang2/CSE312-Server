import json

class Response:
    def __init__(self):
        pass

    def set_status(self, code, text):
        pass

    def headers(self, headers):
        pass

    def cookies(self, cookies):
        pass

    def bytes(self, data):
        pass

    def text(self, data):
        pass

    def json(self, data):
        pass

    def to_data(self):
        pass

def test1():
    res = Response() 
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello'
    acutal = res.to_data()
    assert acutal == expected

if __name__ == '__main__':
    test1()