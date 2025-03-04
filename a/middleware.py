class DisableHTTPSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_secure = lambda: False
        return self.get_response(request) 