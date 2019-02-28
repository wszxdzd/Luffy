
from django.conf.urls import url,include
from django.contrib import admin
from django.views.static import serve
from Luffy import settings
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/',include('course.urls') ),
    url(r'^api/account/',include('aboutaccount.urls') ),
    url(r'^api/pay/',include('pay.urls') ),
# media路径配置
    url(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
]
