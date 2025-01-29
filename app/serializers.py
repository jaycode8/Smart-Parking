from rest_framework.serializers import ModelSerializer
from .models import Users
from django.contrib.auth.hashers import make_password

class UsersSerializers(ModelSerializer):
    class Meta(object):
        model = Users
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password = make_password(password)
        instance = super().create(validated_data)
        instance.password = hashed_password
        instance.is_active = True
        instance.save()
        return instance