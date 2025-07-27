from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status, mixins, generics, permissions, filters
from . import serializers
from .models import Post, Like, Comment
from accounts import permissions as my_permissions

# Create your views here.


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created').select_related('user')
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created', 'title']
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, my_permissions.IsOwnerOrReadOnly,]
    queryset = Post.objects.all().select_related('user')
    serializer_class = serializers.PostDetailSerializer

class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created :
            return Response({'detail':'Post liked!', 'likes_count':post.like_set.count() },status=status.HTTP_201_CREATED)
        else :
            return Response({'detail':'You already liked this post.', 'likes_count':post.like_set.count()}, status=status.HTTP_200_OK)
    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted :
            return Response({'detail':'Post unliked!', 'likes_count':post.like_set.count()}, status=status.HTTP_200_OK)
        return Response({'detail':'Not Liked', 'likes_count':post.like_set.count()}, status=status.HTTP_404_NOT_FOUND)





class PostCommentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    serializer_class = serializers.CommentSerializer
    # serializer_class = serializers.CommentSerializer(many=True, context={'request': request, 'post':post })
    # we use this way to add context to serializers in simple APIViews
    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])
    def get_queryset(self):
        comments = Comment.objects.all().select_related('user', 'parent').filter(post=self.get_post()).order_by('-created')
        return comments
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post=self.get_post())



    # in generics and Viewsets, context with request, view and format automatically will be added to context and for extra data should override blow def
    def get_serializer_context(self):
        tmp = super().get_serializer_context()
        tmp['post'] = self.get_post()
        return tmp

class PostCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,my_permissions.IsOwnerOrReadOnly]
    # queryset = Comment.objects.all().select_related('user')
    serializer_class = serializers.CommentDetailSerializer
    lookup_url_kwarg = 'comment_id'
    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])
    def get_serializer_context(self):
        tmp = super().get_serializer_context()
        tmp['post'] = self.get_post()
        return tmp
    def get_queryset(self):
        comments = Comment.objects.filter(post=self.kwargs['post_id']).order_by('-created').select_related('user', 'post')
        return comments



