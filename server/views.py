from utils.baseclasses import BaseAPIView
from account.decorators import cq_permission_required
from account.models import User
from .statistics import Statistics


class ServerAPI(BaseAPIView):
    @cq_permission_required
    def post(self, request):
        data = request.data
        user = User.objects.get(username=request.query_params['username'])
        statistic = Statistics(user)
        if data['post_type'] == 'message' and data['message_type'] == 'group':
            statistic.handle_message(data)
        elif data['post_type'] == 'message' and data['message_type'] == 'private':
            statistic.handle_private(data, user)
        elif data['post_type'] == 'notice':
            statistic.handle_group(data)
        return self.success("Success")
