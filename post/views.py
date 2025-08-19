from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, mixins, generics, permissions, filters

from accounts.models import Follow
from . import serializers
from .models import Post, Like, Comment
from accounts import permissions as my_permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse



# region PostListCreateView - ListCreate - generics
@extend_schema_view(
    get=extend_schema(
        tags=['Posts - post'],
        description='View all posts',
        responses=serializers.PostSerializer(many=True),
    ),
    post=extend_schema(
        tags=['Posts - post'],
        description='Create a new post',
        request=serializers.PostCreateSerializer,
        responses=serializers.PostCreateSerializer,

        examples=[
            OpenApiExample(
                'Simple Post Example',
                value={
                    'title' : 'My post title',
                    'content' : 'My post content',

                }
            )
        ]

    )
)
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created').select_related('user')
    # serializer_class = serializers.PostSerializer  # just for get
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created', 'title']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.PostCreateSerializer
        return serializers.PostSerializer

    """
    there is two ways to set different serializers for different methods:
        1- create def get_serializer_class(self) and return different serializers for different methods in request
        2- override post/get() method and use @extend_schema() decorator to set serializers 
        
    """

    # @extend_schema(
    #     request=serializers.PostCreateSerializer,
    #     responses=serializers.PostCreateSerializer
    # )
    # def post(self, request, *args, **kwargs):
    #     return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
# endregion

# region PostDetailView - RetrieveUpdateDestroy - generics
@extend_schema_view(
    get=extend_schema(
        tags=['Posts - post'],
        description='Retrieve a post with specific id in url',
        responses=serializers.PostDetailSerializer
    ),
    put=extend_schema(
        tags=['Posts - post'],
        description='Update a post with specific id in url - title and content are needed',
        request=serializers.PostDetailSerializer,
        examples=[
            OpenApiExample(
                'Simple Post Example for update',
                value={
                    'title' : 'My post title',
                    'content' : 'My post content',
                }
            )
        ]
    ),
    patch=extend_schema(
        tags=['Posts - post'],
        description='Update a post with specific id in url - just changed fields are needed',
        request=serializers.PostDetailSerializer,
        examples=[
            OpenApiExample(
                'Simple Post Example to update just title',
                value={'title' : 'My post title'}
            ),
            OpenApiExample(
                'Simple Post Example to update just content',
                value={'content' : 'My post content'}
            ),
            OpenApiExample(
                'Simple Post Example to update all fields',
                value={'title' : 'My post title', 'content' : 'My post content'}
            ),


        ]
    ),
    delete=extend_schema(
        tags=['Posts - post'],
        description='Delete a post with specific id in url',
    )
)
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, my_permissions.IsOwnerOrReadOnly, ]
    queryset = Post.objects.all().select_related('user')
    serializer_class = serializers.PostDetailSerializer
# endregion

# region PostLike - Like(post) Unlike(delete) - APIView
# region schema PostLike
@extend_schema_view(
    post=extend_schema(
        tags=['Likes - post'],
        description='Like a post (by ID)',
        responses={
            201: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Post liked successfully.',
                examples=[
                    OpenApiExample(
                        'Post liked',
                        value={
                            "detail": "Post liked!",
                            "likes_count": 5
                        },
                        status_codes=["201"]
                    )
                ]
            ),
            200: OpenApiResponse(
                description='Post was already liked.',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Already liked',
                        value={
                            "detail": "You already liked this post.",
                            "likes_count": 5
                        },
                        status_codes=["200"]
                    )
                ]
            ),
        }
    ),
    delete=extend_schema(
        tags=['Likes - post'],
        description='Unlike a post (by ID)',
        responses={
            200: OpenApiResponse(
                description='Post unliked successfully.',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Post unliked',
                        value={
                            "detail": "Post unliked!",
                            "likes_count": 4
                        },
                        status_codes=["200"]
                    )
                ]
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='You had not liked this post.',
                examples=[
                    OpenApiExample(
                        'Not liked yet',
                        value={
                            "detail": "Not Liked",
                            "likes_count": 4
                        },
                        status_codes=["404"]
                    )
                ]
            )
        }
    )
)
# endregion
class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({'detail': 'Post liked!', 'likes_count': post.like_set.count()},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'You already liked this post.', 'likes_count': post.like_set.count()},
                            status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted:
            return Response({'detail': 'Post unliked!', 'likes_count': post.like_set.count()},
                            status=status.HTTP_200_OK)
        return Response({'detail': 'Not Liked', 'likes_count': post.like_set.count()}, status=status.HTTP_404_NOT_FOUND)
# endregion

# region CommentList - ListCreate - generics
@extend_schema_view(
    get=extend_schema(
        tags=['Comment - post'],
        description='Retrieve all comments of a post',
        responses=serializers.CommentSerializer(many=True),
    ),
    post=extend_schema(
        tags=['Comment - post'],
        description='Comment for a post (by ID)',
        request=serializers.CommentSerializer,
        responses=serializers.CommentSerializer,
        examples=[
            OpenApiExample(
                'Simple Comment Example',
                description='Keep parent value NULL',
                value={
                    'content' : 'My comment',
                    'parent' : ''
                }
            ),
            OpenApiExample(
                'Simple Replay Example',
                value={
                    'content' : 'My replay',
                    'parent' : '5'
                }
            )
        ]
    ),
)
class PostCommentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = serializers.CommentSerializer

    # serializer_class = serializers.CommentSerializer(many=True, context={'request': request, 'post':post })
    # we use this way to add context to serializers in simple APIViews
    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_queryset(self):
        comments = Comment.objects.all().select_related('user', 'parent').filter(post=self.get_post()).order_by(
            '-created')
        return comments

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post=self.get_post())

    # in generics and Viewsets, context with request, view and format automatically will be added to context and for extra data should override blow def
    def get_serializer_context(self):
        tmp = super().get_serializer_context()
        tmp['post'] = self.get_post()
        return tmp
# endregion

# region CommentDetail - RetrieveUpdateDestroy - generics
# region schema
@extend_schema_view(
    get=extend_schema(
        tags=['Comment - post'],
        description='retrieve a comment (by post_id and comment id)',
        responses=serializers.CommentDetailSerializer
    ),
    put=extend_schema(
        tags=['Comment - post'],
        description='update a comment (by post_id and comment id) - content and parent are needed',
        request=serializers.CommentDetailSerializer,
        examples=[
            OpenApiExample(
                'Simple Comment Example to update',
                value={
                    'parent': '5',
                    'content': 'My comment content',
                }
            )
        ]
    ),
    patch=extend_schema(
        tags=['Comment - post'],
        description='update a comment (by post_id and comment id) - just changed fields are needed',
        request=serializers.CommentDetailSerializer,
        examples=[
            OpenApiExample(
                'Simple Comment Example to update just parent',
                value={'parent': 'My comment parent'}
            ),
            OpenApiExample(
                'Simple Comment Example to update just content',
                value={'content': 'My comment content'}
            ),
            OpenApiExample(
                'Simple Comment Example to update all fields',
                value={'parent': 'My comment parent', 'content': 'My comment content'}
            ),

        ]

    ),
    delete=extend_schema(
        tags=['Comment - post'],
        description='delete a comment (by post_id and comment id)',

    )
)
# endregion
class PostCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, my_permissions.IsOwnerOrReadOnly]
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
        comments = Comment.objects.filter(post=self.kwargs['post_id']).order_by('-created').select_related('user',
                                                                                                           'post')
        return comments

# endregion

# region ProfilePostListView - all post of logged-in user - url is in accounts app urls
@extend_schema(
    tags=['Profile - post'],
    description='All user posts',
               )
class ProfilePostListView(generics.ListCreateAPIView):
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
# endregion

# region ProfilePostDetailView - logged-in users post (by url) - url is in accounts app urls
@extend_schema(tags=['Profile - accounts'])
class ProfilePostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
# endregion

# region ProfileOtherPostListView - all posts of other users - (username in url) - url is in accounts app urls
@extend_schema(tags=['Profile others - accounts'])
class ProfileOtherPostListView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(user = user)
# endregion

# region feed - filter post by whoever is in following
class PostFeedView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    def get_queryset(self):
        following_users = Follow.objects.filter(follower=self.request.user).values_list('following', flat=True)
        posts = Post.objects.filter(user__in = following_users).select_related('user').order_by('-created')
        return posts


