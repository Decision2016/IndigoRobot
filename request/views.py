from utils.baseclasses import BaseAPIView
from account.models import User
from uestc.models import UestcStu
from uestc.portal import Portal


class TaskViewAPI(BaseAPIView):

    def get(self, request):
        users = User.objects.all()
        for user in users:
            try:
                stuInfo = user.stuInfo
            except UestcStu.DoesNotExist:
                continue
            if stuInfo.gradeSpySwitch:
                portal = Portal(user)
                portal.task()
        return self.success({
            'status': 'success'
        })

