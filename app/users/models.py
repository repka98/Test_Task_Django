from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserClient(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	surname = models.CharField(max_length=100)