from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Task, TaskComment
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    PasswordChangeSerializer,
    AccountDeleteSerializer,
    TaskSerializer,
    TaskCommentSerializer,
)
from .permissions import IsStaff, IsStaffOrOwner

from .crypto_utils import encrypt_json


class AuthViewSet(viewsets.ViewSet):
    """
    Frontend bozulmasın diye path'leri aynı tutuyoruz:

    POST /api/register/
    POST /api/login/
    POST /api/logout/
    GET  /api/me/
    POST /api/profile/update/
    POST /api/password/change/
    POST /api/account/delete/
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "success": True,
                "user": {"id": user.id, "username": user.username, "email": user.email},
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""

        if not username or not password:
            return Response(
                {"success": False, "error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"success": False, "error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(
            {
                "success": True,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="logout",
    )
    def logout(self, request):
        logout(request)
        return Response({"success": True})

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        u = request.user

        plain = {
            "isAuthenticated": True,
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
        }

        return Response(encrypt_json(plain))

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="profile/update",
    )
    def profile_update(self, request):
        serializer = ProfileUpdateSerializer(
            instance=request.user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        u = serializer.save()
        return Response(
            {
                "success": True,
                "user": {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                },
            }
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="password/change",
    )
    def password_change(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        login(request, request.user)
        return Response({"success": True})

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="account/delete",
    )
    def account_delete(self, request):
        serializer = AccountDeleteSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        u = request.user
        logout(request)
        u.delete()
        return Response({"success": True})


class UserViewSet(viewsets.ModelViewSet):
    """
    GET    /api/users/?q=...
    POST   /api/users/
    DELETE /api/users/<id>/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaff]

    def get_queryset(self):
        qs = User.objects.filter(is_staff=False, is_superuser=False).order_by("id")
        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(username__icontains=q)
            )
        return qs


class TaskViewSet(viewsets.ModelViewSet):
    """
    GET    /api/tasks/?all=1
    POST   /api/tasks/
    PUT    /api/tasks/<id>/
    DELETE /api/tasks/<id>/
    """
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "retrieve"]:
            permission_classes = [IsAuthenticated, IsStaffOrOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def get_queryset(self):
        show_all = self.request.query_params.get("all") == "1"
        qs = Task.objects.select_related("owner").order_by("id")

        if self.request.user.is_staff or show_all:
            return qs

        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        owner = serializer.validated_data.get("owner", None)
        if self.request.user.is_staff and owner is not None:
            serializer.save(owner=owner)
        else:
            serializer.save(owner=self.request.user)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    GET    /api/tasks/<task_id>/comments/
    POST   /api/tasks/<task_id>/comments/
    PUT    /api/tasks/<task_id>/comments/<id>/
    DELETE /api/tasks/<task_id>/comments/<id>/
    """
    serializer_class = TaskCommentSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsStaffOrOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        return (
            TaskComment.objects.select_related("author")
            .filter(task_id=task_id)
            .order_by("created_at")
        )

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_id")
        serializer.save(task_id=task_id, author=self.request.user)
