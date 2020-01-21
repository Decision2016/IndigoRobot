from django.db import models
from account.models import User


# Create your models here.

class serverInfo(models.Model):
    serverUrl = models.TextField(null=True)
    serverPort = models.IntegerField(null=True)
    serverGroup = models.IntegerField(null=True)
    serverPingSwitch = models.BooleanField(default=False, null=True)
    belong = models.OneToOneField(User, related_name='mcservers', on_delete=models.SET_NULL, null=True)