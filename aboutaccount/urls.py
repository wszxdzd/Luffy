
from django.conf.urls import url
from aboutaccount import views

urlpatterns = [
    url(r'^reg/$', views.RegisterView.as_view()),
    url(r'^login/$', views.LoginView.as_view() ),

    # url(r'^detailcourse/(?P<id>\d+)', views.DetailCourseView.as_view() ),

]
