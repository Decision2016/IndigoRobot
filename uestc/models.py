from django.db import models
from account.models import User
# Create your models here.


class UestcStu(models.Model):
    stuCookies = models.TextField(null=True)
    loginStatus = models.BooleanField(default=False)
    loginHint = models.BooleanField(default=False)
    gradeSpySwitch = models.BooleanField(default=False)
    lastQueryTime = models.DateTimeField(null=True)
    belong = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='stuInfo', null=True)


class Course(models.Model):
    courseName = models.TextField()
    courseId = models.TextField()
    courseGrade = models.TextField()
    coursePoint = models.TextField(default=0)
    belong = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='course', null=True)
