from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status, mixins, generics, permissions

from .models import Follow
from .permissions import IsNotAuthenticated, IsOwnerOrReadOnly
from post import serializers as post_serializers
from . import serializers
from post.models import Post

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse


# Create your views here.


# region Signup
@extend_schema_view(
    post = extend_schema(
       tags=['Enter - accounts'],
        description='Singup new user',
        request=serializers.UserCreateSerializer,
        responses=serializers.UserCreateSerializer,
        examples=[
            OpenApiExample(
                'Simple User info to signup',
                value={
                    'username': 'Kevin',
                    'password': '12345678',
                    'confirm_password': '12345678',
                }
            )
        ]
    ),
)
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserCreateSerializer
    permission_classes = (IsNotAuthenticated,)

# endregion

# region Logout
@extend_schema_view(
    post = extend_schema(
       tags=['Enter - accounts'],
        description='Logout user - (If user is logged in)',


    ),
)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'detail':'Logged out successfully.'},status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
# endregion

# region Profile template with pure APIView
# class ProfileView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     def get(self, request):
#         serializer = serializers.ProfileSerializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         serializer = serializers.ProfileSerializer(request.user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
#         else :
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# endregion
# region Profile - retrieve, update(put, patch)
@extend_schema_view(
    get=extend_schema(
        tags=['Profile - accounts'],
        description='Retrieve logged-in user profile',
        responses=serializers.ProfileSerializer
    ),
    put=extend_schema(
        tags=['Profile - accounts'],
        description='Update logged-in user profile - all details needed',
        request=serializers.ProfileSerializer,
        examples=[
            OpenApiExample(
                'Simple Post Example to update',
                value={
                    'username' : '<USERNAME>',
                    'firstname' : '<FIRSTNAME>',
                    'lastname' : '<LASTNAME>',
                    'email' : '<EMAIL>',
                }
            )
        ]
    ),
    patch=extend_schema(
        tags=['Profile - accounts'],
        description='Update logged-in user profile - just changed details needed',
        request=serializers.ProfileSerializer,
        examples=[
            OpenApiExample(
                'Simple Post Example to update',
                value={
                    'username' : '<USERNAME>',
                    'firstname' : '<FIRSTNAME>',
                    'lastname' : '<LASTNAME>',
                    'email' : '<EMAIL>',
                }
            )
        ]
    ),
)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self):
        return self.request.user
# endregion

# region profile - delete
@extend_schema(
    tags=['Profile - accounts'],
    description='Delete logged-in user profile',
)
class ProfileDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def delete(self, request):
        request.user.delete()
        return Response({'detail':'User deleted.'}, status=status.HTTP_200_OK)
# endregion

# region change password
@extend_schema(
    tags=['Profile - accounts'],
    description='Change password of user',
    request=serializers.ChangePasswordSerializer,
    examples=[
        OpenApiExample(
            'Change Password example',
            value={
                'old_password': '<OLD_PASSWORD>',
                'new_password': '<NEW_PASSWORD>',
                'confirm_password': '<NEW_PASSWORD>',
            }
        )
    ],
    responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Password Changed',
                examples=[
                    OpenApiExample(
                        'Password Changed',
                        status_codes=["200"]
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Error in changing password - bad request',
                response=serializers.ChangePasswordSerializer,
                examples=[
                    OpenApiExample(
                        'Error in changing password - bad request',
                        status_codes=["400"],
                    )
                ]
            ),
        }
)
class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def patch(self, request):
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Password changed.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# endregion

# region ProfilePostListView - All logged in user posts
@extend_schema(
    tags=['Profile - accounts'],
    description='All user posts',
               )
class ProfilePostListView(generics.ListCreateAPIView):
    serializer_class = post_serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
# endregion

# region ProfilePostDetailView - logged in users post (by url)
@extend_schema(tags=['Profile - accounts'])
class ProfilePostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = post_serializers.PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
# endregion

# region Others profile - (username in url)
@extend_schema(tags=['Profile others - accounts'])
class ProfileOtherView(APIView):
    def get (self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = serializers.ProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
# endregion

# region ProfileOtherPostListView - all posts of other users - (username in url)
@extend_schema(tags=['Profile others - accounts'])
class ProfileOtherPostListView(generics.ListAPIView):
    serializer_class = post_serializers.PostSerializer
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(user = user)
# endregion

# region list of followers of one user - (username in url)
@extend_schema(tags=['Follow - accounts'])
class FollowersView(generics.ListAPIView):
    serializer_class = serializers.FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Follow.objects.filter(following=user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        count = self.get_queryset().count()
        return Response(
            {
                'followers_count': count,
                'followers':response.data
            }
        )
# endregion

# region list of followings of one user - (username in url)
@extend_schema(tags=['Follow - accounts'])
class FollowingView(generics.ListAPIView):
    serializer_class = serializers.FollowingSerializer
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Follow.objects.filter(follower=user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        count = self.get_queryset().count()
        return Response(
            {
                'following_count': count,
                'following':response.data
            }
        )
# endregion

# region Follow (post) and Unfollow (delete) a user - (user in url)
@extend_schema(tags=['Follow - accounts'])
class FollowView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, username):

        following_instance = get_object_or_404(User, username=username)
        if following_instance == request.user:
            return Response({'detail': "You can't follow yourself!"}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=following_instance)
        if created:
            return Response({'detail':f'{following_instance} followed!'},status=status.HTTP_202_ACCEPTED)

        else:
            return Response({'detail':f'{following_instance} is already in following.'},status=status.HTTP_200_OK)

    def delete(self, request, username):
        following_instance = get_object_or_404(User, username=username)
        deleted, _ = Follow.objects.filter(follower=request.user, following=following_instance).delete()
        if deleted :
            return Response({'detail':f'{following_instance} unfollowed!'}, status=status.HTTP_200_OK)
        return Response({'detail':f'You were not following {following_instance}!'}, status=status.HTTP_404_NOT_FOUND)
# endregion


