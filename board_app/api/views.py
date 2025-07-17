from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ..models import Board



class BoardViews(APIView):
    serializer_class = BoardSerializer

    def get(self, request):
        boards = Board.objects.all()  # oder .filter(owner=request.user)
        serializer = BoardSerializer(boards, many=True)
        print(boards)
        return Response(serializer.data)









