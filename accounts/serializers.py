from django.contrib.auth.models import User
from .models import Follow
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password')

    def validate(self, data):
        confirm_password = data['confirm_password']

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")

        if confirm_password != data['password']:
            raise serializers.ValidationError("Passwords do not match")

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(username=validated_data['username'],)
        user.set_password(validated_data['password'])
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    is_follower = serializers.SerializerMethodField()
    is_me = serializers.SerializerMethodField()
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('username', 'first_name', 'last_name', 'email', 'is_following', 'is_follower', 'is_me')
        read_only_fields = ('is_following', 'is_follower', 'is_me')

    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user == obj
        return False
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj :
            return obj.following.filter(follower=request.user).exists()
        return False

    def get_is_follower(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj :
            return obj.follower.filter(following=request.user).exists()
        return False


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class FollowerSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Follow
        fields = ('follower',)



class FollowingSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = Follow
        fields = ('following',)
