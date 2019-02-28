from rest_framework import serializers
from course.models import Account
import hashlib
class AccountSerallizer(serializers.ModelSerializer):
    class Meta:
        model =Account
        fields='__all__'

    def create(self, validated_data):
        username =validated_data["username"]
        pwd=validated_data["pwd"]
        hash_pwd =hashlib.md5(pwd.encode()).hexdigest()
        user_obj=Account.objects.create(username=username,pwd=hash_pwd)
        return user_obj