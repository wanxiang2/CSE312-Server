import json


class Response:
    def __init__(self):
        self.response_line = b"HTTP/1.1 200 OK\r\n"
        self.content_type_header = b"Content-Type:text/plain; charset=utf-8\r\n"
        self.content_length_header = b""
        self.x_content_type_options_header = b"X-Content-Type-Options:nosniff\r\n"
        self.response_headers = b""
        self.cookie_headers = b""
        self.response_body = b""

    def set_status(self, code, text):
        status = "HTTP/1.1 " + str(code) + " "  + text + "\r\n"
        self.response_line = status.encode()
        return self

    def headers(self, headers):
        next_headers = ""
        my_content_type = ""

        for key, value in headers.items():

            #print(str(key))

            if key.strip().lower() == "content-type":
                my_content_type = "Content-Type:" + value + "\r\n"
                self.content_type_header = my_content_type.encode()
                continue
            elif key.strip().lower() == "content-length":
                continue
            elif key.strip().lower() == "x-content-type-options":
                continue
            
            next_headers = next_headers + key + ":" + value + "\r\n"
        
        self.response_headers = self.response_headers + next_headers.encode()

        return self

    def cookies(self, cookies):
        next_cookie = ""
        for key, value in cookies.items():
            next_cookie = next_cookie + "Set-Cookie:" + key + "=" + value + "\r\n"

        self.cookie_headers += next_cookie.encode()
        return self

    def bytes(self, data):
        self.response_body = self.response_body + data
        return self

    def text(self, data):
        my_content_type = "Content-Type:text/plain; charset=utf-8\r\n"
        self.content_type_header = my_content_type.encode()

        self.response_body = self.response_body + data.encode()
        return self

    def json(self, data):
        my_content_type = "Content-Type:application/json\r\n"
        self.content_type_header = my_content_type.encode()

        json_body = json.dumps(data, default=str)
        self.response_body = json_body.encode()
        return self

    def to_data(self):
        
        length = str(len(self.response_body))
        self.content_length_header = b"Content-Length:" + length.encode() + b"\r\n"

        # print("\n\n\nPrinting the Response Class!!!!!!\n")
        # print(self.response_line.decode() + self.content_type_header.decode() + self.content_length_header.decode() + self.x_content_type_options_header.decode() + self.response_headers.decode() + self.cookie_headers.decode())

        return self.response_line + self.content_type_header + self.content_length_header + self.x_content_type_options_header + self.response_headers + self.cookie_headers + b"\r\n" + self.response_body
        


def test1():
    res = Response()
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()

def test2():
    res = Response()
    message = "Hi! I'm doing my HW."
    length = str(len(message))
    res.text(message)
    res.headers({"Content-Length": length})

    expected = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 20\r\nX-Content-Type-Options: nosniff\r\n\r\nHi! I'm doing my HW."

    actual = res.to_data()

    # print(expected)
    # print(actual)

    #assert expected==actual

def test3():
    res = Response()
    message = "Hi! I'm doing my HW."
    res.text(message)
    print(res.to_data())

def test4():
    res = Response()
    my_headers = {"Date": "Tue, 13 Feb 2025 08:47:22 GMT", "Server": "Apache/2.4.41 (Ubuntu)", "Content-Type": "text/html; charset=UTF-8", "Connection": "keep-alive", "Cache-Control": "no-cache, no-store"}
    res.headers(my_headers)

    my_cookies1 = {"id": "fhghvndjffj8"}
    res.cookies(my_cookies1)

    my_cookies2 = {"session": "girjfuUUNDJjfnf7"}
    res.cookies(my_cookies2)

    message = "Hey! I am taking Web Apps, Operating Systems, Modern Networking Concepts, and Algorithms. What about you?"

    message = message.encode()

    res.bytes(message)

    print(res.to_data())

def test5():
    res = Response()
    my_headers = {"Date": "Tue, 13 Feb 2025 08:47:22 GMT", "Server": "Apache/2.4.41 (Ubuntu)"}
    res.headers(my_headers)
    my_headers2 = {"Content-Type": "text/html; charset=UTF-8", "Connection": "keep-alive", "Cache-Control": "no-cache, no-store"}

    res.headers(my_headers2)

    my_cookies1 = {"id": "fhghvndjffj8"}
    res.cookies(my_cookies1)

    my_cookies2 = {"session": "girjfuUUNDJjfnf7"}
    res.cookies(my_cookies2)

    message = "Hey! I am taking Web Apps, Operating Systems, Modern Networking Concepts, and Algorithms. What about you?"

    message = message.encode()

    res.bytes(message)

    json_body = [1, 2, 3, 4, 5]

    res.json(json_body)

    print(res.to_data())

def test6():
    res = Response()
    res.set_status(403, "Forbidden")

    my_headers = {"Date": "Tue, 13 Feb 2025 08:47:22 GMT", "Server": "Apache/2.4.41 (Ubuntu)"}
    res.headers(my_headers)
    my_headers2 = {"Content-Type": "text/plain; charset=UTF-8", "Connection": "keep-alive", "Cache-Control": "no-cache, no-store"}

    res.headers(my_headers2)

    my_cookies1 = {"id": "fhghvndjffj8"}
    res.cookies(my_cookies1)

    my_cookies2 = {"session": "girjfuUUNDJjfnf7; Max-Age=3600; HttpOnly"}
    res.cookies(my_cookies2)

    message = "Hey! I am taking Web Apps, Operating Systems, Modern Networking Concepts, and Algorithms. What about you?"

    res.text(message)

    json_body = [1, 2, 3, 4, 5]

    res.json(json_body)

    print(res.to_data())

def test7():
    res = Response()
    res.set_status(403, "Forbidden")

    my_headers = {"Date": "Tue, 13 Feb 2025 08:47:22 GMT", "Server": "Apache/2.4.41 (Ubuntu)"}
    res.headers(my_headers)
    my_headers2 = {"Content-Type": "text/plain; charset=UTF-8", "Connection": "keep-alive", "Cache-Control": "no-cache, no-store"}

    res.headers(my_headers2)

    my_cookies1 = {"id": "fhghvndjffj8"}
    res.cookies(my_cookies1)

    my_cookies2 = {"session": "girjfuUUNDJjfnf7; Max-Age=3600; HttpOnly"}
    res.cookies(my_cookies2)

    message = "Hey! I am taking Web Apps, "
    message2 = "Operating Systems, ".encode()
    message3 = "Modern Networking Concepts, and Algorithms. What about you?"

    res.text(message)
    res.bytes(message2)
    res.text(message3)

    print(res.to_data())

def test8():
    res = Response()
    my_headers = {}
    my_headers["Content-Type"] = "text/javascript"
    res.headers(my_headers)

    my_cookies1 = {"id": "fhghvndjffj8"}
    res.cookies(my_cookies1)

    my_cookies2 = {"session": "girjfuUUNDJjfnf7; Max-Age=3600; HttpOnly"}
    res.cookies(my_cookies2)

    message = "const greet = name => ".encode()
    message2 = "console.log(`Hello, ${name}!`); ".encode()
    message3 = "greet('Alice');".encode()

    message4 = " This is the end."

    res.bytes(message)
    res.bytes(message2)
    res.bytes(message3)
    res.text(message4)

    print(res.to_data())

def test9():
    res = Response()
    my_headers = {}
    my_headers["Content-Type"] = "text/javascript"
    res.headers(my_headers)

    my_cookies1 = {"id": "fhghvndjffj8", "session": "girjfuUUNDJjfnf7; Max-Age=3600; HttpOnly", "user": "gfnfndh; Max-Age=200"}
    res.cookies(my_cookies1)

    my_cookies2 = {"admin": "girjfu8839Jjfnf7; Max-Age=100000; HttpOnly", "id_admin": "=X6kAwpgW29M; Expires=Wed, 7 Feb 2024 16:35:00 GMT"}
    res.cookies(my_cookies2)

    message = "const greet = name => ".encode()
    message2 = "console.log(`Hello, ${name}!`); ".encode()
    message3 = "greet('Alice');".encode()

    message4 = " This is the end."

    res.bytes(message)
    res.bytes(message2)
    res.bytes(message3)
    res.text(message4)

    print(res.to_data())

def test10():
    res = Response()
    my_headers = {}
    #my_headers["Content-Type"] = "text/html; charset=utf-8"
    my_headers["Content-Length"] = "2"
    my_headers["X-Content-Type-Options"] = "nosniff"
    message = "<h1>Hi it's me.</h1>"

    res.headers(my_headers)
    res.text(message)

    my_cookie = {"session": "girjfuUUNDiiivgnjfnf7; Max-Age=3600"}
    res.cookies(my_cookie)

    print(res.to_data())

def test11():
    res = Response()
    message = "Hello! 😄"
    res.text(message)

    my_cookie = {"session": "girjfuUUNDiiivgnjfnf7; Max-Age=3600"}
    res.cookies(my_cookie)

    print(res.to_data())



if __name__ == '__main__':
    test1()
    #test2()
    print("\n")
    test3()
    print("\n")
    test4()
    print("\n")
    test5()
    print("\n")
    test6()
    print("\n")
    test7()
    print("\n")
    test8()
    print("\n")
    test9()
    print("\n")
    test10()
    print("\n")
    test11()


#Write a test case where you create Response and add all headers, cookies, body and then print out the Response and see if it matches.
# Index out of bounds error is due to how you are structuring your Response headers.

# What if you called headers() multiple times with the same header in both? What do we need to do? DO you test for this?