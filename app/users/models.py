from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserClient(models.Model):
	name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	surname = models.CharField(max_length=100)

	def __str__(self):
		return f"{self.last_name} {self.name} {self.surname}"
