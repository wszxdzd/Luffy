from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from . import models
from .serializer import CategorySerializer,CourseSerializer,DetailCourseSerializer
from rest_framework.response import Response
# Create your views here.
class CategoryCourse(APIView):


    def get(self,request):
        queryset=models.Category.objects.all()
        ser_obj=CategorySerializer(queryset,many=True)

        # print(ser_obj.data,type(ser_obj.data))
        return Response(ser_obj.data)


class CourseView(APIView):
    def get(self,request):
        category_id = request.query_params.get("category_id", 0)
        category_id = int(category_id)
        if not category_id:
            queryset=models.Course.objects.all().order_by('order')
        else:
            queryset=models.Course.objects.filter(category_id=category_id).order_by('order')
        ser_obj =CourseSerializer(queryset,many=True)
        return Response(ser_obj.data)


class DetailCourseView(APIView):
    def get(self,reuqest,id):
        course_detail_obj=models.CourseDetail.objects.filter(id=id).first()
        ser_obj =DetailCourseSerializer(course_detail_obj)
        return Response(ser_obj.data)




        





