from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Passwords don’t match'})

        account = User(
            username=self.validated_data['email'],
            fullname=self.validated_data['fullname'],
            email=self.validated_data['email']
        )
        account.set_password(pw)
        account.save()
        return account
    





    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = email
    password = serializers.CharField(write_only=True)

    class Meta: 
        fields = ['email', 'password']