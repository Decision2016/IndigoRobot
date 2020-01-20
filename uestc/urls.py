from django.conf.urls import url
from .views import StuInfoAPI

urlpatterns = [
    url(r'^portal', StuInfoAPI.as_view())
]