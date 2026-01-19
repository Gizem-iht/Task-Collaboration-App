from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    STATUS_CHOICES = [
        ("TODO", "Yapılacak"),
        ("IN_PROGRESS", "Devam Ediyor"),
        ("BLOCKED", "Engellendi"),
        ("DONE", "Tamamlandı"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True) 
    state = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="TODO",
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.state}"


class TaskComment(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       
        return f"{self.author.username} kullanıcısının yorumu"