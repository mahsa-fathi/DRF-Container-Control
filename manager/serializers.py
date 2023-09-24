from rest_framework import serializers
from .models import Application, RunLog


class AppSerializer(serializers.ModelSerializer):
    command = serializers.CharField(allow_blank=True)

    class Meta:
        model = Application
        fields = ["id", "name", "image", "envs", "command", "created_at"]


class RunLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunLog
        fields = ["id", "application", "container_name", "envs", "command", "logs", "executed_at"]
