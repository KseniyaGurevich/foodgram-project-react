from .models import User, Follow
from djoser.serializers import UserSerializer


class CurrentUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "password")
        extra_kwargs = {'password': {'write_only': True}}

