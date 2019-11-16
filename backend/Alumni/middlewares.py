from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
class MyTest(MiddlewareMixin):
    def process_response(self, request:HttpRequest, response):
        if request.method == "OPTIONS":
            response.status_code = 200
        response['Access-Control-Allow-Origin'] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, HEAD"
        response["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"
        return response

