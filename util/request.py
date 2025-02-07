class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        decoded_request = request.decode()
        header_and_body = decoded_request.split("\r\n\r\n")

        request_lines = header_and_body[0].split("\r\n")

        request_line_values = request_lines[0].split()

        self.body = header_and_body[1].encode()
        self.method = request_line_values[0].upper()
        self.path = request_line_values[1]
        self.http_version = request_line_values[2]
        self.headers = {}
        self.cookies = {}

        for header in request_lines[1:]:
            print("1\n")
            i = 0
            
            #print(header + "\n")
            while header[i] != ":":
                #print(header[i] + "\n")
                i += 1

            header_key = header[:i]
            header_value = header[i+1:].lstrip()

            self.headers[header_key] = header_value

    

        


def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct


if __name__ == '__main__':
    test1()
