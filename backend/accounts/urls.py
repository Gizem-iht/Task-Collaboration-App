from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, UserViewSet, TaskViewSet, TaskCommentViewSet

router = DefaultRouter()
router.register(r"", AuthViewSet, basename="auth")    
router.register(r"users", UserViewSet, basename="users")
router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),

    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentViewSet.as_view({"get": "list", "post": "create"}),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:pk>/",
        TaskCommentViewSet.as_view(
            {"put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="task-comment-detail",
    ),
]
