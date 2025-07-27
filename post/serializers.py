from rest_framework import serializers

from post.models import Post, Comment, Like

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Comment
        fields = ('id','content', 'user', 'created','post', 'parent')
        read_only_fields = ('id', 'user', 'created','post')
    def validate_parent(self, value):
        request = self.context.get('request')
        post = self.context.get('post')
        if value and value.post_id != post.pk:
            raise serializers.ValidationError("Parent comment does not belong to this post.")
        return value
class CommentDetailSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta(CommentSerializer.Meta) :
        fields = CommentSerializer.Meta.fields + ('children',)
    def get_children(self, obj):
        descendants = Comment.objects.filter(post=obj.post, parent__isnull=False).select_related('user', 'parent')
        return CommentSerializer(descendants, many=True).data




class CommentFlatSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Comment
        fields = ('id','content', 'user', 'created','post', 'parent')
        read_only_fields = ('id', 'user', 'created','post')


class PostSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('title', 'user', 'detail_url')
        read_only_fields = ('user', 'detail_url')

    def get_detail_url(self, obj):
        request = self.context.get('request')
        if request :
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

class PostDetailSerializer(PostSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    is_liked = serializers.SerializerMethodField()
    comment_set = CommentSerializer(many=True, read_only=True)
    # for nested serializers must use related name for nested field.
    comment_count = serializers.IntegerField(source='comment_set.count', read_only=True)
    like_count = serializers.IntegerField(source='like_set.count', read_only=True)

    class Meta:
        model = Post
        fields = ('title', 'content', 'user' , 'created', 'comment_set', 'comment_count','is_liked', 'like_count')
        read_only_fields = ('user',  'created')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            liked = obj.like_set.filter(user=request.user).exists()
            # liked = Like.objects.filter(post=obj, user=request.user).exists()
            return liked
        return False

