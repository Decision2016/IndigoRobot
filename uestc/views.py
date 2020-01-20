from django.shortcuts import render
from account.decorators import login_required
from utils.baseclasses import BaseAPIView
from .models import UestcStu, Course
from utils.functions import verify_login_status


class StuInfoAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        stuInfo = user.stuInfo
        res_status = verify_login_status(stuInfo.stuCookies)
        return self.success({
            'loginStatus': 'true' if res_status else 'false',
            'lastQueryTime': stuInfo.lastQueryTime
        })
