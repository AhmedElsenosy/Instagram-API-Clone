from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        temp_email = f"{validated_data['username']}@placeholder.local"

        user = User.objects.create_user(
            username=validated_data['username'],
            email=temp_email,
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'image', 'profile_image_url', 'gender', 'is_verified', 'created_at']
        read_only_fields = ['id', 'username', 'is_verified', 'created_at', 'profile_image_url']

    def get_profile_image_url(self, obj):
        return obj.get_profile_image_url()


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if email already exists for another user
        if User.objects.filter(email=value).exclude(id=self.context['user_id']).exists():
            raise serializers.ValidationError("This email is already used by another account.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(id=self.context['user_id'])
        
        # Update user email
        user.email = email
        user.is_verified = True  # Mark as verified when email is added
        user.save()
        
        # Send verification email
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        subject = 'Account Verification - Instagram Clone'
        message = f'''
        Hello {user.username},

        Your account has been successfully verified!

        Your email {user.email} has been added to your Instagram Clone account.

        Thank you for using our platform!

        Best regards,
        Instagram Clone Team
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@instagram-clone.com',
            recipient_list=[user.email],
            fail_silently=False,
        )


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for responses"""
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image_url', 'is_verified']

    def get_profile_image_url(self, obj):
        return obj.get_profile_image_url()