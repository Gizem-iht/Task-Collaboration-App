from rest_framework.permissions import BasePermission


class IsStaff(BasePermission):
    """
    Sadece staff kullanıcılar erişebilir.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsStaffOrOwner(BasePermission):
    """
    Staff her şeye erişebilir.
    Normal user sadece kendi objesine erişebilir.
    (Task.owner / TaskComment.author)
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        if hasattr(obj, "owner_id"):
            return obj.owner_id == request.user.id

        if hasattr(obj, "author_id"):
            return obj.author_id == request.user.id

        return False
