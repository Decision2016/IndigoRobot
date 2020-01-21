from django.conf.urls import url, include
from .views import MCServerAPI

urlpatterns = [
    url(r'^mc', MCServerAPI.as_view())
]