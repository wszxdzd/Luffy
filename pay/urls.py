
from django.conf.urls import url
from pay import views

urlpatterns = [
    url(r'^shop_car/$', views.Shopping_car.as_view()),
    url(r'^account_car/$', views.AccountView.as_view()),
    url(r'^paymennt/$', views.PaymentView.as_view()),


    # url(r'^detailcourse/(?P<id>\d+)', views.DetailCourseView.as_view() ),

]
