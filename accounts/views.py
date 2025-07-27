from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status, mixins, generics, permissions
from .permissions import IsNotAuthenticated, IsOwnerOrReadOnly
from post import serializers as post_serializers
from . import serializers
from post.models import Post

# Create your views here.


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserCreateSerializer
    permission_classes = (IsNotAuthenticated,)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'detail':'Logged out successfully.'},status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        serializer = serializers.ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = serializers.ProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ProfileDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def delete(self, request):
        request.user.delete()
        return Response({'detail':'User deleted.'}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def patch(self, request):
        serializer = serializers.ResetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Password changed.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfilePostListView(generics.ListCreateAPIView):
    serializer_class = post_serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfilePostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = post_serializers.PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class ProfileOtherView(APIView):
    def get (self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = serializers.ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileOtherPostListView(generics.ListAPIView):
    serializer_class = post_serializers.PostSerializer
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(user = user)
