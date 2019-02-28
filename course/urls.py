
from django.conf.urls import url
from course import views

urlpatterns = [
    url(r'^category/$', views.CategoryCourse.as_view() ),
    url(r'^course/$', views.CourseView.as_view() ),
    url(r'^detailcourse/(?P<id>\d+)', views.DetailCourseView.as_view() ),

]
