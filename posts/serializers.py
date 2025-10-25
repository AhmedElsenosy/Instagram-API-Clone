from rest_framework import serializers
from django.conf import settings
from .models import Post, PostMedia, Like, Comment, CommentLike

User = settings.AUTH_USER_MODEL


# -----------------------------------------
# Basic User Serializer (for references)
# -----------------------------------------
class UserPublicSerializer(serializers.Serializer):
    """Public user info serializer (used inside other serializers)"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True, required=False)


# -----------------------------------------
# Post Media Serializer
# -----------------------------------------
class PostMediaSerializer(serializers.ModelSerializer):
    """Serializer for post media files (image/video)"""
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'type']


# -----------------------------------------
# Comment Like Serializer (optional detail)
# -----------------------------------------
class CommentLikeSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'created_at']


# -----------------------------------------
# Comment Serializer (supports nested replies)
# -----------------------------------------
class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments and replies"""
    author = UserPublicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'content',
            'parent_comment',
            'replies',
            'likes_count',
            'created_at',
        ]
        read_only_fields = ['author', 'post', 'replies', 'likes_count']

    def get_replies(self, obj):
        """Return nested replies for each comment"""
        replies_qs = obj.replies.all()
        return CommentSerializer(replies_qs, many=True).data

    def get_likes_count(self, obj):
        """Return number of likes for the comment"""
        return obj.likes.count()

    def create(self, validated_data):
        """Create comment or reply with author/post from context"""
        user = self.context['request'].user
        post = self.context['post']

        # ✅ Remove parent_comment to avoid passing it twice
        parent_comment = validated_data.pop('parent_comment', None)

        return Comment.objects.create(
            author=user,
            post=post,
            parent_comment=parent_comment,
            **validated_data
        )


# -----------------------------------------
# Like Serializer (used for debugging or count)
# -----------------------------------------
class LikeSerializer(serializers.ModelSerializer):
    """Serializer for post likes"""
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']


# -----------------------------------------
# Post Serializer
# -----------------------------------------
class PostSerializer(serializers.ModelSerializer):
    """Main post serializer with nested media, likes, and comments"""
    author = UserPublicSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'caption',
            'media',
            'likes_count',
            'comments',
            'created_at',
        ]
        read_only_fields = ['author', 'media', 'likes_count', 'comments']

    def get_likes_count(self, obj):
        """Return total likes for the post"""
        return obj.likes.count()

    def get_comments(self, obj):
        """Return top-level comments only (exclude replies)"""
        qs = obj.comments.filter(parent_comment__isnull=True)
        return CommentSerializer(qs, many=True).data

    def create(self, validated_data):
        """
        Create a post and handle uploaded media files.
        Author is passed from the view via serializer.save(author=request.user)
        """
        post = Post.objects.create(**validated_data)  # ✅ no author here

        # Handle uploaded media files if any
        request = self.context.get('request')
        if request and hasattr(request, 'FILES'):
            media_files = request.FILES.getlist('media')
            for f in media_files:
                PostMedia.objects.create(post=post, file=f)

        return post
