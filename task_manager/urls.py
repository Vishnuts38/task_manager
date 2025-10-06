# file: taskmanager/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet, CustomObtainAuthToken,PrivateGraphQLView
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", CustomObtainAuthToken.as_view(), name="api-token"),
    path("api/", include(router.urls)),
    path("graphql/", PrivateGraphQLView.as_view(graphiql=True)),  
    
]
