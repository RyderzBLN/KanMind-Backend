from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import RegistrationSerializer
from .serializers import LoginSerializer
from django.contrib.auth import get_user_model


class RegistrationView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            
            saved_account = serializer.save() 
            print(saved_account)
            token, created = Token.objects.get_or_create(user=saved_account)  


            data = {
                'token': token.key,
                'fullname': saved_account.fullname,
                'email': saved_account.email,
                'user_id': saved_account.id

            }
            return Response(data, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class CustomLoginView(APIView):
    serializer = LoginSerializer() 
    permission_classes = [AllowAny]

    def post(self, request):
        if serializer.is_valid():
            email = request.data.get('email')
            password = request.data.get('password')


        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Ungültige Login-Daten'}, status=401)

        if not user.check_password(password):
            return Response({'error': 'Ungültige Login-Daten'}, status=401)

        # Token erstellen oder holen
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'fullname': getattr(user, 'fullname', ''),
            'email': user.email,
            'user_id': user.id
        }, status=200)
