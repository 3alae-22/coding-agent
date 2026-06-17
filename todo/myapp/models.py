from django.db import models
from django.utils import timezone


class Todo(models.Model):
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', '-priority', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

    @property
    def priority_order(self):
        order = {self.PRIORITY_HIGH: 0, self.PRIORITY_MEDIUM: 1, self.PRIORITY_LOW: 2}
        return order.get(self.priority, 1)
