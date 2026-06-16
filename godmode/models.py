from django.db import models
from django.utils import timezone

# Create your models here.
class Expense(models.Model):
    name = models.CharField(max_length=50, default="expense")
    description = models.TextField(default="")
    date = models.DateTimeField(default=timezone.now)
    price = models.IntegerField(default=0)