from django.shortcuts import render
from utils.baseclasses import BaseAPIView
from utils.functions import send_group_message
from account.decorators import login_required
from .models import serverInfo
from .serializer import ServerInfoSerializer
from .StatusPing import StatusPing

class MCServerAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        try:
            server_info = user.mcservers
        except serverInfo.DoesNotExist:
            server_info = serverInfo.objects.create()
            server_info.belong = user
        server_info.save()
        return self.success(ServerInfoSerializer(server_info).data)

    @login_required
    def put(self, request):
        user = request.user
        data = request.data
        try:
            server_info = user.mcservers
        except serverInfo.DoesNotExist:
            server_info = serverInfo.objects.create()
            server_info.belong = user
        server_info.serverUrl = data['serverUrl']
        server_info.serverPort = data['serverPort']
        server_info.serverGroup = data['serverGroup']
        server_info.serverPingSwitch = data['serverPingSwitch']
        server_info.save()
        return self.success('success')


class MinecraftServerControl(object):
    def __init__(self, user):
        self.user = user

    def command_analyse(self, command_string, **kwargs):
        command_array = command_string.split(" ")
        if command_array[0] == '/mc':
            try:
                server_info = self.user.mcservers
            except serverInfo.DoesNotExist:
                send_group_message('服务器信息未设置', kwargs['group_id'], self.user.cqUrl)
                return
            if server_info.serverGroup == kwargs['group_id'] and server_info.serverPingSwitch:
                serverStatus = StatusPing(host=server_info.serverUrl, port=server_info.serverPort).get_status()
                player_list = serverStatus['players']
                msg = ''
                if player_list['online'] == 0:
                    msg = '服务器最大在线人数：{0}，现在服务器中没有人哦~'.format(player_list['max'])
                else:
                    msg = '服务器最大在线人数：{0}，当前服务器在线人数:{1},在线玩家列表'.format(player_list['max'], player_list['online'])
                    for sample in player_list['sample']:
                        msg += '\n' + sample['name']
                send_group_message(msg, kwargs['group_id'], self.user.cqUrl)
        elif command_array[0] == '/switch_mc' and kwargs['user_id']:
            try:
                server_info = self.user.mcservers
            except serverInfo.DoesNotExist:
                send_group_message('服务器信息未设置', kwargs['group_id'], self.user.cqUrl)
                return
            server_info.serverPingSwitch = not server_info.serverPingSwitch
            server_info.save()
            send_group_message('服务器信息接口状态已调整：{0}'.format('ON' if server_info.serverPingSwitch else 'OFF'), kwargs['group_id'], self.user.cqUrl)

