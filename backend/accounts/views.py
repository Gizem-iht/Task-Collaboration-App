import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Task, TaskComment


# ========== AUTH ==========

@csrf_exempt
def register_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return JsonResponse({"error": "All fields are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "This username is already taken"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "This email is already in use"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        status=201,
    )


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {"success": False, "error": "Invalid credentials"},
            status=401,
        )

    login(request, user)

    return JsonResponse(
        {
            "success": True,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }
    )


@csrf_exempt
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return JsonResponse({"success": True})


def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False}, status=401)

    u = request.user
    return JsonResponse(
        {
            "isAuthenticated": True,
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
        }
    )


# ========== USERS (ADMIN PANELİ) ==========

@csrf_exempt
def users_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if not request.user.is_staff:
        return JsonResponse({"error": "Only staff can use this endpoint"}, status=403)

    # GET -> list + search (adminler listede görünmesin)
    if request.method == "GET":
        q = request.GET.get("q", "").strip()

        users = User.objects.filter(is_staff=False, is_superuser=False)
        if q:
            users = users.filter(
                Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(username__icontains=q)
            )

        users = users.order_by("id")

        data = []
        for u in users:
            data.append(
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "is_staff": u.is_staff,
                    "is_active": u.is_active,
                }
            )

        return JsonResponse(data, safe=False)

    # POST -> admin yeni user oluştursun
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()

        if not username or not email or not password:
            return JsonResponse(
                {"error": "Username, email and password are required"}, status=400
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "This username is already taken"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "This email is already in use"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        return JsonResponse(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_active": user.is_active,
                },
            },
            status=201,
        )

    return JsonResponse({"error": "Only GET and POST are allowed"}, status=405)


@csrf_exempt
def user_detail_view(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if not request.user.is_staff:
        return JsonResponse({"error": "Only staff can use this endpoint"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if request.method == "DELETE":
        user.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Only DELETE is allowed"}, status=405)


# ========== TASKS ==========

VALID_STATES = {"TODO", "IN_PROGRESS", "BLOCKED", "DONE"}


@csrf_exempt
def tasks_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # GET -> listeleme
    if request.method == "GET":
        show_all = request.GET.get("all") == "1"

        # /api/tasks/?all=1  --> herkes tüm taskları görür
        # /api/tasks/        --> admin: tümü, user: sadece kendisi
        if request.user.is_staff or show_all:
            qs = Task.objects.select_related("owner").all()
        else:
            qs = Task.objects.select_related("owner").filter(owner=request.user)

        data = []
        for t in qs.order_by("id"):
            data.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "state": t.state,
                    "owner_id": t.owner_id,
                    "owner_username": t.owner.username if t.owner else "",
                }
            )

        return JsonResponse(data, safe=False)

    # POST -> yeni task oluştur
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        state = data.get("state", "TODO").strip() or "TODO"
        owner_id = data.get("owner_id")

        if not title:
            return JsonResponse({"error": "Title is required"}, status=400)

        if state not in VALID_STATES:
            return JsonResponse({"error": "Invalid state"}, status=400)

        # admin ise owner_id ile başka birine assign edebilir
        if request.user.is_staff and owner_id:
            try:
                owner = User.objects.get(id=owner_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Owner not found"}, status=404)
        else:
            owner = request.user

        task = Task.objects.create(
            title=title,
            description=description,
            state=state,
            owner=owner,
        )

        return JsonResponse(
            {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "state": task.state,
                    "owner_id": task.owner_id,
                    "owner_username": task.owner.username,
                },
            },
            status=201,
        )

    return JsonResponse({"error": "Only GET and POST are allowed"}, status=405)


@csrf_exempt
def task_detail_view(request, task_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        task = Task.objects.select_related("owner").get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    # GET: herkes görebilir (login olmak şart)
    # PUT/DELETE: sadece owner veya admin
    if request.method in ("PUT", "DELETE"):
        if not request.user.is_staff and task.owner_id != request.user.id:
            return JsonResponse({"error": "Not allowed"}, status=403)

    if request.method == "GET":
        return JsonResponse(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "state": task.state,
                "owner_id": task.owner_id,
                "owner_username": task.owner.username if task.owner else "",
            }
        )

    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        state = data.get("state", task.state).strip() or task.state

        if not title:
            return JsonResponse({"error": "Title is required"}, status=400)

        if state not in VALID_STATES:
            return JsonResponse({"error": "Invalid state"}, status=400)

        task.title = title
        task.description = description
        task.state = state
        task.save()

        return JsonResponse(
            {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "state": task.state,
                    "owner_id": task.owner_id,
                    "owner_username": task.owner.username if task.owner else "",
                },
            }
        )

    if request.method == "DELETE":
        task.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Only GET, PUT and DELETE are allowed"}, status=405)


# ========== COMMENTS ==========

@csrf_exempt
def task_comments_view(request, task_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    # GET -> herkes görebilir (login yeter)
    if request.method == "GET":
        qs = TaskComment.objects.select_related("author").filter(task=task).order_by(
            "created_at"
        )
        data = []
        for c in qs:
            data.append(
                {
                    "id": c.id,
                    "author_id": c.author_id,
                    "author_username": c.author.username if c.author else "",
                    "content": c.content,
                    "created_at": c.created_at.isoformat(),
                }
            )
        return JsonResponse(data, safe=False)

    # POST -> herkes comment atabilir (login yeter)
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)

        c = TaskComment.objects.create(
            task=task, author=request.user, content=content
        )

        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "id": c.id,
                    "author_id": c.author_id,
                    "author_username": c.author.username,
                    "content": c.content,
                    "created_at": c.created_at.isoformat(),
                },
            },
            status=201,
        )

    return JsonResponse({"error": "Only GET and POST are allowed"}, status=405)


@csrf_exempt
def task_comment_detail_view(request, task_id, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    try:
        comment = TaskComment.objects.select_related("author").get(
            id=comment_id, task=task
        )
    except TaskComment.DoesNotExist:
        return JsonResponse({"error": "Comment not found"}, status=404)

    if not (request.user.is_staff or comment.author_id == request.user.id):
        return JsonResponse({"error": "Not allowed"}, status=403)

    if request.method in ("PUT", "PATCH"):
        try:
            data = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)

        comment.content = content
        comment.save()

        return JsonResponse(
            {
                "id": comment.id,
                "author_id": comment.author_id,
                "author_username": comment.author.username,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
            }
        )

    if request.method == "DELETE":
        comment.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Only PUT, PATCH and DELETE are allowed"}, status=405)


# ========== PROFILE / PASSWORD / ACCOUNT DELETE ==========

@csrf_exempt
def update_profile_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip().lower()

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    if (
        email
        and User.objects.filter(email=email)
        .exclude(id=request.user.id)
        .exists()
    ):
        return JsonResponse({"error": "This email is already in use"}, status=400)

    u = request.user
    u.first_name = first_name
    u.last_name = last_name
    u.email = email
    u.save()

    return JsonResponse(
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


@csrf_exempt
def password_change_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    old_password = data.get("old_password", "")
    new_password1 = data.get("new_password1", "")
    new_password2 = data.get("new_password2", "")

    if not old_password or not new_password1 or not new_password2:
        return JsonResponse(
            {"error": "All password fields are required"}, status=400
        )

    if new_password1 != new_password2:
        return JsonResponse({"error": "New passwords do not match"}, status=400)

    u = request.user
    if not u.check_password(old_password):
        return JsonResponse({"error": "Current password is incorrect"}, status=400)

    u.set_password(new_password1)
    u.save()

    login(request, u)

    return JsonResponse({"success": True})


@csrf_exempt
def account_delete_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    password = data.get("password", "")

    if not password:
        return JsonResponse({"error": "Password is required"}, status=400)

    u = request.user
    if not u.check_password(password):
        return JsonResponse({"error": "Password is incorrect"}, status=400)

    logout(request)
    u.delete()

    return JsonResponse({"success": True})
