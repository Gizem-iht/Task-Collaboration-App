from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    STATE_TODO = "TODO"
    STATE_IN_PROGRESS = "IN_PROGRESS"
    STATE_BLOCKED = "BLOCKED"
    STATE_DONE = "DONE"

    STATE_CHOICES = [
        (STATE_TODO, "TODO"),
        (STATE_IN_PROGRESS, "IN PROGRESS"),
        (STATE_BLOCKED, "BLOCKED"),
        (STATE_DONE, "DONE"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default=STATE_TODO,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.state})"


class TaskComment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task_id}"
