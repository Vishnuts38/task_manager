import graphene
from graphene_django import DjangoObjectType
from .models import Task
from .serializers import TaskSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")        

class TaskType(DjangoObjectType):
    
    assignedTo = graphene.Field(UserType, source='assigned_to')
    class Meta:
        model = Task
        fields = ("id", "title", "status", "created_at", "assigned_to")

class Query(graphene.ObjectType):
    tasks = graphene.List(TaskType)

    def resolve_tasks(self, info):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise Exception("Authentication required")
        return Task.objects.filter(assigned_to=user).order_by("-created_at")


class CreateTask(graphene.Mutation):
    task = graphene.Field(TaskType)
    ok = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        status = graphene.String(required=False)

    def mutate(self, info, title, status=None):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise Exception("Authentication required")
        data = {"title": title}
        if status:
            data["status"] = status
        serializer = TaskSerializer(data=data, context={"request": info.context})
        serializer.is_valid(raise_exception=True)
        serializer.save(assigned_to=user)
        return CreateTask(task=serializer.instance, ok=True)

class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
