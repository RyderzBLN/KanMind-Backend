from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save() 
            token, created = Token.objects.get_or_create(user=saved_account)  


            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email
            }
            return Response(data, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.permissions import IsAuthenticated

class MyPrivateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'data': 'Hello, authenticated user!'})