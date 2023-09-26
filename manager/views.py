from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
import docker

from .models import Application, RunLog
from .serializers import AppSerializer, RunLogsSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = AppSerializer

    def destroy(self, request, *args, **kwargs):
        """
        destroy removes all the containers of application and then calls super().destroy
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        client = docker.from_env()
        containers = client.containers.list()
        instance = self.get_object()
        image_name = instance.image
        if ':' not in instance.image:
            image_name = instance.image + ":latest"

        for container in containers:
            if image_name in container.image.tags:
                try:
                    container.remove(force=True)
                except docker.errors.APIError as e:
                    # if containers could not be stopped an error will be returned
                    return Response(data={"details": f"Error removing container {container.name}: {str(e)}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return super().destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        This action lists all applications with a count of data.
        It overrides the list action by adding count to the base result
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = super().list(request, *args, **kwargs)
        response_data = {
            'count': len(response.data),
            'results': response.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        This action handles listing the history of runs for a specific application id
        :param request:
        :param pk:
        :return:
        """
        try:
            queryset = RunLog.objects.filter(application_id=pk)
            serializer = RunLogsSerializer(queryset, many=True)
        except Exception as e:
            return Response(data={'details': str(e)}, status=status.HTTP_404_NOT_FOUND)
        response_data = {
            'count': len(serializer.data),
            'results': serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def run(self, request, pk=None):
        """
        This action handle run API for specific application
        :param request:
        :param pk:
        :return:
        """
        client = docker.from_env()
        instance = self.get_object()

        if instance is None:
            # return 404 if application id was incorrect
            return Response({"details": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        image_name = instance.image
        if ':' not in instance.image:
            # adding latest tag to image
            image_name = instance.image + ":latest"

        try:
            client.images.pull(repository=image_name)
        except docker.errors.APIError as e:
            # return 500 if image name was incorrect or any other problems for pulling the image
            return Response(data={"details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        log = RunLog(application=instance)
        log.save()

        try:
            # Run the container
            container_name = instance.name + '_' + str(int(datetime.now().timestamp()))
            container = client.containers.run(image=image_name,
                                              name=container_name,
                                              environment=instance.envs,
                                              command=instance.command,
                                              detach=True)
            log.status = RunLog.Status.FINISHED  # changing status of run log to finished
            log.container_name = container_name
            log.logs = container.logs().decode('utf-8')
            log.save()

            # Count the number of containers with the same image
            num_containers = len([c for c in client.containers.list() if c.image.tags[0] == image_name])
        except Exception as e:
            # Returning 500 if there was any problem for running the container
            log.status = RunLog.Status.FAILED  # changing status of run log to failed
            log.save()
            return Response(data={"details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data={"details": "Successful",
                              "containerName": container_name,
                              "logs": container.logs().decode('utf-8'),
                              "numContainers": num_containers},
                        status=status.HTTP_200_OK)
