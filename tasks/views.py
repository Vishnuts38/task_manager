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