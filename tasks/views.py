from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from rest_framework.authentication import TokenAuthentication
from .models import Task
from .serializers import TaskSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny    
from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
User = get_user_model()

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        return Task.objects.filter(assigned_to=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        
        serializer.save(assigned_to=self.request.user)


class CustomObtainAuthToken(ObtainAuthToken):

    permission_classes = [AllowAny]  
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    


@method_decorator(csrf_exempt, name="dispatch")
class PrivateGraphQLView(GraphQLView):

    def dispatch(self, request, *args, **kwargs):

        try:
            auth_result = TokenAuthentication().authenticate(request)
            if auth_result is not None:
                request.user, request.auth = auth_result
        except Exception:
            pass

        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication credentials were not provided.")
        return super().dispatch(request, *args, **kwargs)
    

class CreateSuperUserView(APIView):
    # Only superusers can create another superuser
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "User already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        return Response(
            {
                "message": "Superuser created successfully.",
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )