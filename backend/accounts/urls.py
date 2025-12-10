from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.me_view, name="me"),


    path("profile/update/", views.update_profile_view, name="update_profile"),
    path("password/change/", views.password_change_view, name="password_change"),
    path("account/delete/", views.account_delete_view, name="account_delete"),


    path("users/", views.users_view, name="users_list"),
    path("users/<int:user_id>/", views.user_detail_view, name="user_detail"),

    
    path("tasks/", views.tasks_view, name="tasks"),
    path("tasks/<int:task_id>/", views.task_detail_view, name="task_detail"),
    path(
        "tasks/<int:task_id>/comments/",
        views.task_comments_view,
        name="task_comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        views.task_comment_detail_view,
        name="task_comment_detail",
    ),
]
