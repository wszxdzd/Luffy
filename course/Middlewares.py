from django.utils.deprecation import MiddlewareMixin

class Mymiddle(MiddlewareMixin):
    def process_response(self,request,response):
        response["Access-Control-Allow-Origin"] = "*"
        if request.method == "OPTIONS":
            # 复杂请求会先发预检
            response["Access-Control-Allow-Headers"] = "Content-Type,AUTHENICATE"
            response["Access-Control-Allow-Methods"] = "PUT,PATCH,DELETE"

        return response