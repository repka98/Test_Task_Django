from django.db import models
from app.users.models import UserClient
# Create your models here.

class Application(models.Model):
	number_app = models.CharField(max_length=12)
	user_app = models.OneToOneField(UserClient, on_delete=models.CASCADE)
