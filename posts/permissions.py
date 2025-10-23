from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allow full access only to the author.
    Other users can only read (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) are allowed for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the object
        return obj.author == request.user


class IsCommentOwnerOrPostOwner(permissions.BasePermission):
    """
    Allow comment deletion only by the comment author or the post author.
    """

    def has_object_permission(self, request, view, obj):
        # Allow all safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # If the user is the comment author → allowed
        if obj.author == request.user:
            return True

        # If the user is the post author → allowed
        if obj.post.author == request.user:
            return True

        # Otherwise → deny access
        return False
