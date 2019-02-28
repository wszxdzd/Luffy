from rest_framework import serializers
from . import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model =models.Category
        fields = "__all__"

class CourseSerializer(serializers.ModelSerializer):
    course_img =serializers.SerializerMethodField()
    level =serializers.CharField(source="get_level_display")
    price=serializers.SerializerMethodField()
    
    def get_price(self,obj):
        price_obj=obj.price_policy.all().order_by("price").first()
        return price_obj.price

    def get_course_img(self,obj):
        return "http://127.0.0.1:8000/media/" + str(obj.course_img)

    class Meta:
        model =models.Course
        fields=["id","title","course_img","brief","level","study_num","is_free","price"]


class DetailCourseSerializer(serializers.ModelSerializer):
    title=serializers.SerializerMethodField()
    level =serializers.SerializerMethodField()
    study_num =serializers.SerializerMethodField()
    recommend_course =serializers.SerializerMethodField()
    teachers=serializers.SerializerMethodField()
    price=serializers.SerializerMethodField()
    outline=serializers.SerializerMethodField()


    def get_outline(self,obj):
        return [ {"id":item.id,"title":item.title,"content":item.content} for item in obj.course_outline.all().order_by("order")]
    def get_price(self,obj):
        return [ {"id": item.id, "valid_period": item.get_valid_period_display(), "price": item.price} for item in obj.course.price_policy.all().order_by("price")]
    def get_teachers(self,obj):
        return [{"id":item.id,"name":item.name} for item in obj.teachers.all()]
    def get_recommend_course(self,obj):
        return [ {"id":item.id,"title":item.title} for item in obj.recommend_courses.all()]
    def get_study_num(self,obj):
        return obj.course.study_num
    def get_level(self,obj):
        return obj.course.get_level_display()
    def get_title(self,obj):
        return obj.course.title

    class Meta:
        model =models.CourseDetail
        exclude=['course']