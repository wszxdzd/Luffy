from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AccountSerallizer
from course.models import Account
import uuid
from utils.Base_code import Base_statue_code

# Create your views here.
class RegisterView(APIView):
    def post(self,request):
        ser_obj =AccountSerallizer(data=request.data)
        if ser_obj.is_valid():
            ser_obj.save()
            return Response("注册成功")
        return Response(ser_obj.errors)


class LoginView(APIView):
    def post(self,request):
        ret=Base_statue_code()
        username =request.data.get('username','')
        if not username:
            ret.code = 1010
            ret.error = "用户名不能为空"
        pwd=request.data.get('pwd','')
        if not pwd:
            ret.code = 1011
            ret.error = "密码不能为空"
        try:

            user_obj=Account.objects.filter(username=username,pwd=pwd).first()
            if not user_obj:
                ret.code = 1012
                ret.error = "用户名或密码错误"
                return Response(ret.dict)
            user_obj.token=uuid.uuid4()
            user_obj.save()
            ret.data="登录成功"

        except Exception as e:
            ret.code=1013
            ret.data="登录失败"
        return Response(ret.dict)

