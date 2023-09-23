from .models import Application, RunLog
from .serializers import AppSerializer, RunLogsSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import docker


class ApplicationApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppSerializer
    queryset = Application.objects.all()

    def delete(self, request, *args, **kwargs):
        client = docker.from_env()
        containers = client.containers.list()
        instance = self.get_object()

        # Iterate through containers and stop those with the specified image name
        for container in containers:
            if instance.name in container.image.tags:
                try:
                    container.stop()
                except docker.errors.APIError as e:
                    return Response(data={"details": f"Error stopping container {container.name}: {e}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return super().delete(request, *args, **kwargs)


class ApplicationListApiView(generics.ListAPIView):
    queryset = Application.objects.all()
    serializer_class = AppSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response_data = {
                'count': len(response.data),
                'results': response.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return response


class RunLogsListApiView(generics.ListAPIView):
    queryset = RunLog.objects.all()
    serializer_class = RunLogsSerializer

    def get_queryset(self):
        app_id = self.kwargs.get('id')
        queryset = RunLog.objects.filter(application_id=app_id)
        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response_data = {
                'count': len(response.data),
                'results': response.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return response


class BuildApplicationApiView(generics.CreateAPIView):
    serializer_class = AppSerializer


@api_view(['GET'])
def run_app(request, pk):
    client = docker.from_env()

    details = Application.objects.filter(pk=pk).first()

    if details is None:
        return Response({"details": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

    image_name = details.image

    try:
        client.images.pull(repository=image_name)
    except docker.errors.APIError as e:
        return Response(data={"details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    log = RunLog(application=details)
    log.save()

    try:
        # Run the container
        container = client.containers.run(image=image_name,
                                          environment=details.envs,
                                          command=details.command,
                                          detach=True)
        log.status = RunLog.Status.FINISHED
        log.container_name = container.name
        log.logs = container.logs().decode('utf-8')
        log.save()

        # Count the number of containers with the same image
        num_containers = len([c for c in client.containers.list() if c.image.tags[0] == image_name])

        details.no_containers = num_containers
        details.save()
    except Exception as e:
        log.status = RunLog.Status.FAILED
        log.save()
        return Response(data={"details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(data={"details": "Successful",
                          "logs": container.logs().decode('utf-8'),
                          "NumContainers": num_containers},
                    status=status.HTTP_200_OK)
