from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Application(models.Model):
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=100)
    envs = models.JSONField()
    command = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"


class RunLog(models.Model):
    class Status(models.TextChoices):
        FINISHED = "FIN", _("Finished")
        RUNNING = "RUN", _("Running")
        FAILED = "FAI", _("Failed")

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    container_name = models.CharField(max_length=100, null=True)
    envs = models.JSONField()
    command = models.TextField()
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.RUNNING)
    logs = models.TextField(null=True)
    executed_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.status == self.Status.RUNNING:
            if not self.envs:
                self.envs = self.application.envs
            if not self.command:
                self.command = self.application.command
        super().save(*args, **kwargs)

    def __str__(self):
        return f"run for {self.application.name} at {self.executed_at}"
