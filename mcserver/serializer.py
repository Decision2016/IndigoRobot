from rest_framework import serializers


class ServerInfoSerializer(serializers.Serializer):
    serverUrl = serializers.CharField()
    serverPort = serializers.IntegerField()
    serverGroup = serializers.IntegerField()
    serverPingSwitch = serializers.BooleanField()