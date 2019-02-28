from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from course.models import Account
import datetime
from django.utils.timezone import now

class Myauth(BaseAuthentication):
    def authenticate(self, request):
        if request.method == "OPTIONS":
            return None
        token=request.META.get('HTTP_AUTHENICATE')
        if not token:
            raise AuthenticationFailed({"code": 1020, "error": "没有携带token"})
        user_obj =Account.objects.filter(token=token).first()
        if not user_obj:
            raise AuthenticationFailed({"code": 1021, "error": "token不合法"})
        oldtime=user_obj.token_create_time
        nowtime=now()+datetime.timedelta(days=1)
        if (nowtime-oldtime).days>7:
            raise AuthenticationFailed({"code": 1022, "error": "token过期请重新登录"})
        return (user_obj,token)