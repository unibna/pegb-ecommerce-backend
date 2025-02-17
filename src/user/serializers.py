
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, UserRole, UserDepartment, UserMembership
from membership.serializers import MembershipSerializer


class UserActivationSerializer(serializers.Serializer):
    activation_token = serializers.UUIDField()
    
    def validate_activation_token(self, value):
        if not User.objects.filter(activation_token=value, is_active=False).exists():
            raise serializers.ValidationError("Invalid or expired activation code.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        if 'password2' in validated_data:
            validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'id': {'read_only': True},
        }
        
    def validate(self, attrs):
        if 'password' in attrs and 'password2' in attrs:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError(
                    {"password": "Password fields didn't match."})
            attrs.pop('password2')
        return attrs


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        exclude = ['user']


class UserRoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('role',)

    def create(self, validated_data):
        user = self.context['request'].user
        user_role = UserRole.objects.create(user=user, **validated_data)
        return user_role


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('is_enabled',)

    def update(self, instance, validated_data):
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.save()
        return instance


class UserDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartment
        exclude = ['user']
        
        
class UserDepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartment
        fields = ('department',)

    def create(self, validated_data):
        user = self.context['request'].user
        return UserDepartment.objects.create(user=user, **validated_data)


class UserDepartmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartment
        fields = ('is_enabled',)

    def update(self, instance, validated_data):
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.save()
        return instance


class UserMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMembership
        exclude = ['user']


class MeSerializer(serializers.ModelSerializer):
    membership = serializers.SerializerMethodField(read_only=True)
    department = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'activation_token')
        
    def get_membership(self, obj):
        try:
            user_membership = obj.membership.get()
            if user_membership.membership:
                return MembershipSerializer(user_membership.membership).data
        except UserMembership.DoesNotExist:
            return None

    def get_department(self, obj):
        try:
            user_department = UserDepartment.objects.filter(
                user=obj,
                is_enabled=True
            ).first()
            if not user_department:
                return None
            if user_department.department:
                return user_department.department.id
        except UserDepartment.DoesNotExist:
            return None
    