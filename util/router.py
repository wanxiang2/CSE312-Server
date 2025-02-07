class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        self.routes.append([method.upper(), path, action, exact_path])

    def route_request(self, request, handler):
        method_of_request = request.method
        path_of_request = request.path

        for route in self.routes:
            if method_of_request == route[0]:
                if route[3] == True:
                    if path_of_request == route[1]:
                        route[2](request, handler)
                        return

                else:
                    if path_of_request.startswith(route[1]):
                        route[2](request, handler)
                        return
                    
        return "404 Not Found"
