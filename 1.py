import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Luffy.settings")
    import django

    django.setup()

    from course import models
    # ret =models.Course.objects.all().values('coursedetail__teachers__name')
    # print(ret)
    # ret=models.CourseDetail.objects.get(id=1)
    # print(ret.teachers,type(ret.teachers))
    # print(ret.teachers.all())
    # ret =models.Teacher.objects.filter(id=1).values('coursedetail__course__title')
    # print(ret)
    # ret1=models.Teacher.objects.filter(coursedetail__course__title= 'python21天入门')
    # print(ret1)


    ret =models.CourseDetail.objects.get(id=1)
    c=ret.teachers.all().values('name')
    print(c,type(c))