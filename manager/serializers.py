from rest_framework import serializers
from .models import Application, RunLog


class AppSerializer(serializers.ModelSerializer):
    command = serializers.CharField(allow_blank=True)
    envs = serializers.JSONField(allow_null=True)

    class Meta:
        model = Application
        fields = ["id", "name", "image", "envs", "command", "no_containers", "created_at"]


class RunLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunLog
        fields = ["id", "application", "envs", "command", "executed_at"]
